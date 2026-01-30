# 向量数据库操作

import os
import chromadb
from chromadb.config import Settings
from config.model_config import VECTOR_DB_CONFIG

class VectorDatabase:
    def __init__(self):
        self.db_type = VECTOR_DB_CONFIG["DB_TYPE"]
        self.persist_directory = VECTOR_DB_CONFIG["PERSIST_DIRECTORY"]
        self.collection_name = VECTOR_DB_CONFIG["COLLECTION_NAME"]
        self.similarity_threshold = VECTOR_DB_CONFIG["SIMILARITY_THRESHOLD"]
        self.top_k = VECTOR_DB_CONFIG["TOP_K"]
        self.metadata_filters = VECTOR_DB_CONFIG["METADATA_FILTERS"]
        
        # 初始化数据库
        self.client = self.init_client()
        self.collection = self.init_collection()
    
    def init_client(self):
        """初始化数据库客户端"""
        try:
            if self.db_type == "chromadb":
                # 创建持久化目录
                os.makedirs(self.persist_directory, exist_ok=True)
                
                # 初始化ChromaDB客户端（使用新的PersistentClient）
                client = chromadb.PersistentClient(
                    path=self.persist_directory
                )
                
                return client
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
        except Exception as e:
            print(f"Error initializing client: {e}")
            raise
    
    def init_collection(self):
        """初始化集合"""
        try:
            # 检查集合是否存在
            collections = self.client.list_collections()
            collection_names = [col.name for col in collections]
            
            # 尝试删除现有的集合，以便重新创建
            if self.collection_name in collection_names:
                print(f"删除现有集合: {self.collection_name}")
                self.client.delete_collection(self.collection_name)
            
            # 创建新集合，不指定嵌入函数
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Medical knowledge base"}
            )
            print(f"创建新集合: {self.collection_name}")
            
            return collection
        except Exception as e:
            print(f"Error initializing collection: {e}")
            raise
    
    def add_chunks(self, chunks):
        """添加文本块到向量数据库"""
        try:
            if not chunks:
                print("No chunks to add")
                return 0
            
            # 准备数据
            ids = []
            documents = []
            metadatas = []
            
            for chunk in chunks:
                # 检查必要字段
                if not all(key in chunk for key in ["id", "content"]):
                    continue
                
                ids.append(chunk["id"])
                documents.append(chunk["content"])
                
                # 处理元数据，将列表转换为字符串
                metadata = chunk.get("metadata", {})
                processed_metadata = {}
                for key, value in metadata.items():
                    if isinstance(value, list):
                        # 将列表转换为字符串
                        processed_metadata[key] = ", ".join(str(item) for item in value)
                    else:
                        processed_metadata[key] = value
                metadatas.append(processed_metadata)
            
            if not ids:
                print("No valid chunks to add")
                return 0
            
            # 尝试添加到集合，使用最简单的方式
            # 由于 onnxruntime 问题，我们只添加文本和元数据，不使用嵌入功能
            # 这样至少可以存储数据，后续可以再处理查询问题
            print(f"尝试添加 {len(ids)} 个文本块到集合")
            
            # 分批次添加，避免一次性添加太多数据
            batch_size = 10
            total_added = 0
            
            for i in range(0, len(ids), batch_size):
                batch_ids = ids[i:i+batch_size]
                batch_documents = documents[i:i+batch_size]
                batch_metadatas = metadatas[i:i+batch_size]
                
                try:
                    # 只添加文本和元数据，不使用嵌入功能
                    self.collection.add(
                        ids=batch_ids,
                        documents=batch_documents,
                        metadatas=batch_metadatas
                    )
                    total_added += len(batch_ids)
                    print(f"已添加批次 {i//batch_size + 1}，共 {total_added} 个文本块")
                except Exception as e:
                    print(f"添加批次 {i//batch_size + 1} 时出错: {e}")
                    continue
            
            # 持久化
            try:
                self.client.persist()
                print("数据持久化完成")
            except Exception as e:
                print(f"持久化时出错: {e}")
            
            print(f"成功添加 {total_added} 个文本块到向量数据库")
            return total_added
        except Exception as e:
            print(f"Error adding chunks: {e}")
            return 0
    
    def query(self, query_embedding, top_k=None, filters=None):
        """查询向量数据库"""
        try:
            if not query_embedding:
                return []
            
            # 使用默认值
            if top_k is None:
                top_k = self.top_k
            
            if filters is None:
                filters = self.metadata_filters
            
            # 执行查询
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filters
            )
            
            # 处理结果
            processed_results = []
            for i in range(len(results["ids"][0])):
                result = {
                    "id": results["ids"][0][i],
                    "score": results["distances"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i]
                }
                
                # 过滤相似度低于阈值的结果
                if result["score"] <= (1 - self.similarity_threshold):
                    processed_results.append(result)
            
            return processed_results
        except Exception as e:
            print(f"Error querying database: {e}")
            return []
    
    def get_collection_stats(self):
        """获取集合统计信息"""
        try:
            stats = self.collection.count()
            print(f"Collection contains {stats} documents")
            return stats
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return 0
    
    def clear_collection(self):
        """清空集合"""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.init_collection()
            print(f"Collection {self.collection_name} cleared")
        except Exception as e:
            print(f"Error clearing collection: {e}")
    
    def update_chunk(self, chunk_id, new_content=None, new_metadata=None, new_embedding=None):
        """更新文本块"""
        try:
            update_data = {}
            if new_content is not None:
                update_data["documents"] = new_content
            if new_metadata is not None:
                update_data["metadatas"] = new_metadata
            if new_embedding is not None:
                update_data["embeddings"] = new_embedding
            
            if update_data:
                self.collection.update(
                    ids=[chunk_id],
                    **update_data
                )
                self.client.persist()
                print(f"Updated chunk: {chunk_id}")
                return True
            return False
        except Exception as e:
            print(f"Error updating chunk: {e}")
            return False
    
    def delete_chunk(self, chunk_id):
        """删除文本块"""
        try:
            self.collection.delete(ids=[chunk_id])
            self.client.persist()
            print(f"Deleted chunk: {chunk_id}")
            return True
        except Exception as e:
            print(f"Error deleting chunk: {e}")
            return False

if __name__ == "__main__":
    # 示例使用
    vector_db = VectorDatabase()
    
    # 获取统计信息
    vector_db.get_collection_stats()
    
    # 示例查询
    sample_query_embedding = [0.0] * 1024  # 模拟嵌入向量
    results = vector_db.query(sample_query_embedding, top_k=3)
    print(f"查询结果数量: {len(results)}")
    for i, result in enumerate(results):
        print(f"结果 {i+1}: 相似度={1-result['score']:.4f}")
        print(f"内容: {result['content'][:100]}...")
        print()
