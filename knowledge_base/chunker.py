# 文本分块器

import re
import uuid
from config.model_config import EMBEDDING_CONFIG

class MedicalChunker:
    def __init__(self):
        self.max_chunk_size = EMBEDDING_CONFIG.get("MAX_LENGTH", 512)
        self.overlap_size = 100
    
    def chunk_document(self, document):
        """对整个文档进行分块"""
        chunks = []
        
        # 处理文档内容
        if document.get('content'):
            for section in document['content']:
                section_chunks = self.chunk_section(section, document)
                chunks.extend(section_chunks)
        
        # 处理表格
        if document.get('tables'):
            for table in document['tables']:
                table_chunks = self.chunk_table(table, document)
                chunks.extend(table_chunks)
        
        return chunks
    
    def chunk_section(self, section, document):
        """对章节进行分块"""
        chunks = []
        content = section.get('content', '')
        section_title = section.get('section', '')
        
        if not content:
            return chunks
        
        # 按医疗文档语义结构切分
        semantic_chunks = self.semantic_split(content)
        
        for i, semantic_chunk in enumerate(semantic_chunks):
                # 检查大小
                if len(semantic_chunk) > self.max_chunk_size:
                    # 进一步切分
                    sub_chunks = self.size_split(semantic_chunk)
                    for j, sub_chunk in enumerate(sub_chunks):
                        # 使用UUID生成唯一ID
                        unique_id = str(uuid.uuid4())[:8]
                        chunk = {
                            "id": f"{document['source']}_{document['filename']}_{unique_id}",
                            "content": sub_chunk,
                            "metadata": {
                                "document_title": document['metadata'].get('title', ''),
                                "section_title": section_title,
                                "source": document['source'],
                                "source_organization": document['metadata'].get('source_organization', ''),
                                "publication_date": document['metadata'].get('publication_date', ''),
                                "authors": document['metadata'].get('authors', []),
                                "chunk_type": "text",
                                "chunk_index": i * 100 + j
                            }
                        }
                        chunks.append(chunk)
                else:
                    # 使用UUID生成唯一ID
                    unique_id = str(uuid.uuid4())[:8]
                    chunk = {
                        "id": f"{document['source']}_{document['filename']}_{unique_id}",
                        "content": semantic_chunk,
                        "metadata": {
                            "document_title": document['metadata'].get('title', ''),
                            "section_title": section_title,
                            "source": document['source'],
                            "source_organization": document['metadata'].get('source_organization', ''),
                            "publication_date": document['metadata'].get('publication_date', ''),
                            "authors": document['metadata'].get('authors', []),
                            "chunk_type": "text",
                            "chunk_index": i
                        }
                    }
                    chunks.append(chunk)
        
        return chunks
    
    def chunk_table(self, table, document):
        """对表格进行分块"""
        chunks = []
        content = table.get('content', '')
        section_title = table.get('section', '')
        
        if not content:
            return chunks
        
        # 表格内容通常较短，直接作为一个块
        chunk = {
            "id": f"{document['source']}_{document['filename']}_table",
            "content": content,
            "metadata": {
                "document_title": document['metadata'].get('title', ''),
                "section_title": section_title,
                "source": document['source'],
                "source_organization": document['metadata'].get('source_organization', ''),
                "publication_date": document['metadata'].get('publication_date', ''),
                "authors": document['metadata'].get('authors', []),
                "chunk_type": "table"
            }
        }
        chunks.append(chunk)
        
        return chunks
    
    def semantic_split(self, text):
        """按语义切分文本"""
        # 医疗文档语义切分规则
        # 1. 按段落切分
        paragraphs = re.split(r'[\n\r]+\s*[\n\r]+', text)
        
        # 2. 按医疗文档结构切分
        semantic_chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # 检查是否为新的语义单元
            if self.is_new_semantic_unit(paragraph):
                if current_chunk:
                    semantic_chunks.append(current_chunk)
                    current_chunk = paragraph
                else:
                    current_chunk = paragraph
            else:
                current_chunk += "\n" + paragraph
        
        if current_chunk:
            semantic_chunks.append(current_chunk)
        
        return semantic_chunks
    
    def is_new_semantic_unit(self, paragraph):
        """判断是否为新的语义单元"""
        # 医疗文档语义单元标识
        semantic_markers = [
            r'^\s*[一二三四五六七八九十]+[、.]',  # 中文数字序号
            r'^\s*\d+[、.]',  # 阿拉伯数字序号
            r'^\s*[A-Za-z]+[、.]',  # 字母序号
            r'^\s*【[^】]+】',  # 中文括号标题
            r'^\s*\([^)]+\)',  # 英文括号标题
            r'^\s*症状[:：]',
            r'^\s*病因[:：]',
            r'^\s*诊断[:：]',
            r'^\s*治疗[:：]',
            r'^\s*用药[:：]',
            r'^\s*剂量[:：]',
            r'^\s*禁忌[:：]',
            r'^\s*注意事项[:：]',
            r'^\s*副作用[:：]',
            r'^\s*预防[:：]',
            r'^\s*饮食[:：]',
            r'^\s*运动[:：]',
            r'^\s*预后[:：]'
        ]
        
        for marker in semantic_markers:
            if re.match(marker, paragraph):
                return True
        
        return False
    
    def size_split(self, text):
        """按大小切分文本"""
        chunks = []
        current_pos = 0
        text_length = len(text)
        max_iterations = 100  # 防止无限循环
        iteration_count = 0
        
        while current_pos < text_length and iteration_count < max_iterations:
            iteration_count += 1
            end_pos = min(current_pos + self.max_chunk_size, text_length)
            
            # 尝试在句子边界切分
            if end_pos < text_length:
                # 寻找最近的句子结束符
                sentence_end = re.search(r'[。！？.!?]\s*', text[current_pos:end_pos][::-1])
                if sentence_end:
                    end_pos = end_pos - sentence_end.start()
            
            # 确保有重叠
            chunk = text[current_pos:end_pos]
            chunks.append(chunk)
            
            # 计算下一个位置，确保前进
            next_pos = end_pos - self.overlap_size
            if next_pos <= current_pos:
                # 如果没有前进，强制前进
                next_pos = end_pos
            current_pos = next_pos
        
        return chunks
    
    def chunk_multiple_documents(self, documents):
        """对多个文档进行分块"""
        all_chunks = []
        
        for document in documents:
            chunks = self.chunk_document(document)
            all_chunks.extend(chunks)
        
        return all_chunks

if __name__ == "__main__":
    # 示例使用
    chunker = MedicalChunker()
    sample_document = {
        "source": "WHO",
        "filename": "diabetes_guide.pdf",
        "metadata": {
            "title": "糖尿病防治指南",
            "authors": ["WHO Expert Group"],
            "publication_date": "2022",
            "source_organization": "WHO"
        },
        "content": [
            {
                "section": "概述",
                "content": "糖尿病是一种慢性疾病，当胰腺不能产生足够的胰岛素或人体不能有效利用所产生的胰岛素时发生。胰岛素是一种调节血糖的激素。高血糖症或血糖升高，是糖尿病失控的常见结果，随着时间的推移会对身体的许多系统造成严重损害，特别是神经和血管。"
            },
            {
                "section": "症状",
                "content": "糖尿病的常见症状包括：多尿、口渴、多食、体重减轻、疲劳、视力模糊、伤口愈合缓慢、反复感染等。如果您出现这些症状，应及时就医。"
            }
        ],
        "tables": []
    }
    
    chunks = chunker.chunk_document(sample_document)
    print(f"生成了 {len(chunks)} 个块")
    for i, chunk in enumerate(chunks):
        print(f"块 {i+1}: {len(chunk['content'])} 字符")
        print(f"内容: {chunk['content'][:100]}...")
        print()
