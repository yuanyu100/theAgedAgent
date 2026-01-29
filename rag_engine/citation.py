# 引用溯源模块

import re
from config.model_config import RAG_CONFIG

class CitationManager:
    def __init__(self):
        self.citation_enabled = RAG_CONFIG["CITATION"]["ENABLED"]
        self.citation_format = RAG_CONFIG["CITATION"]["FORMAT"]
        self.include_url = RAG_CONFIG["CITATION"]["INCLUDE_URL"]
        self.include_author = RAG_CONFIG["CITATION"]["INCLUDE_AUTHOR"]
    
    def extract_citations(self, answer, retrieved_results):
        """提取引用"""
        if not self.citation_enabled:
            return []
        
        citations = []
        
        # 提取文本中的引用标记
        citation_markers = self.extract_citation_markers(answer)
        
        # 为每个引用标记创建引用信息
        for marker in citation_markers:
            index = int(marker) - 1  # 转换为0-based索引
            
            if 0 <= index < len(retrieved_results):
                result = retrieved_results[index]
                citation = self.create_citation(result, index + 1)
                citations.append(citation)
        
        return citations
    
    def extract_citation_markers(self, text):
        """提取文本中的引用标记"""
        # 匹配形如 [1], [2] 等的引用标记
        pattern = r'\[(\d+)\]'
        matches = re.findall(pattern, text)
        
        # 去重并排序
        unique_markers = sorted(set(matches), key=int)
        
        return unique_markers
    
    def create_citation(self, result, citation_number):
        """创建引用信息"""
        metadata = result.get("metadata", {})
        
        citation = {
            "number": citation_number,
            "source": metadata.get("source", ""),
            "document_title": metadata.get("document_title", ""),
            "section_title": metadata.get("section_title", ""),
            "publication_date": metadata.get("publication_date", ""),
            "authors": metadata.get("authors", []),
            "source_organization": metadata.get("source_organization", "")
        }
        
        # 添加URL（如果有）
        if self.include_url and metadata.get("url"):
            citation["url"] = metadata.get("url")
        
        # 添加作者信息（如果有）
        if self.include_author and metadata.get("authors"):
            citation["authors"] = metadata.get("authors")
        
        return citation
    
    def format_citations(self, citations):
        """格式化引用为文本"""
        if not citations:
            return ""
        
        formatted_citations = "\n\n参考资料：\n"
        
        for citation in citations:
            cite_text = f"[{citation['number']}] "
            
            if citation.get("document_title"):
                cite_text += f"{citation['document_title']}. "
            
            if citation.get("authors"):
                authors = ", ".join(citation["authors"])
                cite_text += f"作者：{authors}. "
            
            if citation.get("publication_date"):
                cite_text += f"发布日期：{citation['publication_date']}. "
            
            if citation.get("source"):
                cite_text += f"来源：{citation['source']}. "
            
            if citation.get("url"):
                cite_text += f"链接：{citation['url']}"
            
            formatted_citations += cite_text.strip() + "\n"
        
        return formatted_citations
    
    def add_citations_to_answer(self, answer, retrieved_results):
        """为回答添加引用"""
        if not self.citation_enabled:
            return answer
        
        # 提取引用
        citations = self.extract_citations(answer, retrieved_results)
        
        # 格式化引用
        formatted_citations = self.format_citations(citations)
        
        # 添加到回答末尾
        return answer + formatted_citations

if __name__ == "__main__":
    # 示例使用
    citation_manager = CitationManager()
    
    # 示例回答
    answer = "糖尿病的常见症状包括：多尿、口渴、多食、体重减轻、疲劳、视力模糊、伤口愈合缓慢、反复感染等[1]。如果您出现这些症状，应及时就医[2]。"
    
    # 示例检索结果
    retrieved_results = [
        {
            "id": "1",
            "content": "糖尿病的常见症状包括：多尿、口渴、多食、体重减轻、疲劳、视力模糊、伤口愈合缓慢、反复感染等。",
            "metadata": {
                "source": "WHO",
                "document_title": "糖尿病防治指南",
                "publication_date": "2022",
                "authors": ["WHO Expert Group"],
                "source_organization": "WHO"
            }
        },
        {
            "id": "2",
            "content": "如果出现糖尿病相关症状，应及时就医进行诊断和治疗。",
            "metadata": {
                "source": "中国CDC",
                "document_title": "糖尿病预防与控制",
                "publication_date": "2021",
                "authors": ["中国CDC专家"],
                "source_organization": "中国CDC"
            }
        }
    ]
    
    # 提取引用
    citations = citation_manager.extract_citations(answer, retrieved_results)
    print("提取的引用:")
    for citation in citations:
        print(citation)
    
    # 格式化引用
    formatted_citations = citation_manager.format_citations(citations)
    print("\n格式化的引用:")
    print(formatted_citations)
    
    # 添加引用到回答
    final_answer = citation_manager.add_citations_to_answer(answer, retrieved_results)
    print("\n带引用的回答:")
    print(final_answer)
