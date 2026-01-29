# 多路召回模块

import os
import json
from rank_bm25 import BM25Okapi
import jieba
from knowledge_base.embedder import MedicalEmbedder
from knowledge_base.vector_db import VectorDatabase
from config.model_config import RAG_CONFIG, VECTOR_DB_CONFIG

class MultiRetriever:
    def __init__(self):
        self.multi_retrieval_enabled = RAG_CONFIG["MULTI_RETRIEVAL"]["ENABLED"]
        self.weights = RAG_CONFIG["MULTI_RETRIEVAL"]["WEIGHTS"]
        self.top_k = VECTOR_DB_CONFIG["TOP_K"]
        
        # 初始化嵌入器
        self.embedder = MedicalEmbedder()
        
        # 初始化向量数据库
        self.vector_db = VectorDatabase()
        
        # 初始化BM25（需要构建索引）
        self.bm25 = None
        self.corpus = []
        self.corpus_metadata = []
        self.build_bm25_index()
    
    def build_bm25_index(self):
        """构建BM25索引"""
        try:
            # 从向量数据库获取所有文档
            # 注意：这是一个简化实现，实际应用中可能需要更高效的方式
            # 这里我们假设已经有一个文档集合
            
            # 临时实现：从处理后的数据中加载
            from config.crawler_config import STORAGE_CONFIG
            processed_path = os.path.join(STORAGE_CONFIG["DATA_STORE_PATH"], "processed", "medical_data.json")
            
            if os.path.exists(processed_path):
                with open(processed_path, 'r', encoding='utf-8') as f:
                    documents = json.load(f)
                
                # 构建语料库
                for doc in documents:
                    if doc.get('content'):
                        for section in doc['content']:
                            content = section.get('content', '')
                            if content:
                                self.corpus.append(content)
                                self.corpus_metadata.append({
                                    "document_title": doc['metadata'].get('title', ''),
                                    "section_title": section.get('section', ''),
                                    "source": doc['source'],
                                    "source_organization": doc['metadata'].get('source_organization', ''),
                                    "publication_date": doc['metadata'].get('publication_date', ''),
                                    "authors": doc['metadata'].get('authors', [])
                                })
                
                # 分词
                tokenized_corpus = [list(jieba.cut(doc)) for doc in self.corpus]
                
                # 构建BM25
                self.bm25 = BM25Okapi(tokenized_corpus)
                print(f"BM25索引构建完成，包含 {len(self.corpus)} 个文档")
            else:
                print("未找到处理后的数据，BM25索引构建失败")
        except Exception as e:
            print(f"Error building BM25 index: {e}")
    
    def retrieve(self, query):
        """多路召回"""
        results = []
        
        if self.multi_retrieval_enabled:
            # 向量搜索
            vector_results = self.vector_search(query)
            
            # BM25搜索
            bm25_results = self.bm25_search(query)
            
            # 融合结果
            results = self.fuse_results(vector_results, bm25_results)
        else:
            # 仅使用向量搜索
            results = self.vector_search(query)
        
        return results
    
    def vector_search(self, query):
        """向量搜索"""
        try:
            # 嵌入查询
            query_embedding = self.embedder.embed_query(query)
            if not query_embedding:
                return []
            
            # 查询向量数据库
            results = self.vector_db.query(query_embedding, top_k=self.top_k)
            
            # 格式化结果
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result["id"],
                    "content": result["content"],
                    "score": 1 - result["score"],  # 转换为相似度
                    "metadata": result["metadata"],
                    "type": "vector"
                })
            
            return formatted_results
        except Exception as e:
            print(f"Error in vector search: {e}")
            return []
    
    def bm25_search(self, query):
        """BM25搜索"""
        try:
            if not self.bm25 or not self.corpus:
                return []
            
            # 分词
            tokenized_query = list(jieba.cut(query))
            
            # 搜索
            scores = self.bm25.get_scores(tokenized_query)
            
            # 获取top_k结果
            top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:self.top_k]
            
            # 格式化结果
            formatted_results = []
            for idx in top_indices:
                if scores[idx] > 0:
                    formatted_results.append({
                        "id": f"bm25_{idx}",
                        "content": self.corpus[idx],
                        "score": scores[idx],
                        "metadata": self.corpus_metadata[idx],
                        "type": "bm25"
                    })
            
            return formatted_results
        except Exception as e:
            print(f"Error in BM25 search: {e}")
            return []
    
    def fuse_results(self, vector_results, bm25_results):
        """融合搜索结果"""
        # 结果融合
        fused_results = {}
        
        # 添加向量搜索结果
        for result in vector_results:
            fused_results[result["id"]] = {
                **result,
                "fused_score": result["score"] * self.weights["vector"]
            }
        
        # 添加BM25搜索结果
        for result in bm25_results:
            if result["id"] in fused_results:
                # 已存在，累加分数
                fused_results[result["id"]]["fused_score"] += result["score"] * self.weights["bm25"]
            else:
                # 不存在，创建新条目
                fused_results[result["id"]] = {
                    **result,
                    "fused_score": result["score"] * self.weights["bm25"]
                }
        
        # 按融合分数排序
        sorted_results = sorted(
            fused_results.values(),
            key=lambda x: x["fused_score"],
            reverse=True
        )[:self.top_k]
        
        return sorted_results

if __name__ == "__main__":
    # 示例使用
    retriever = MultiRetriever()
    
    # 测试查询
    query = "糖尿病有哪些症状？"
    results = retriever.retrieve(query)
    
    print(f"查询: {query}")
    print(f"召回结果数量: {len(results)}")
    for i, result in enumerate(results):
        print(f"\n结果 {i+1}:")
        print(f"得分: {result['fused_score'] if 'fused_score' in result else result['score']:.4f}")
        print(f"类型: {result['type']}")
        print(f"内容: {result['content'][:200]}...")
        print(f"来源: {result['metadata'].get('source', '')}")
        print(f"文档标题: {result['metadata'].get('document_title', '')}")
