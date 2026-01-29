# 向量化器

import os
from sentence_transformers import SentenceTransformer
from config.model_config import EMBEDDING_CONFIG

class MedicalEmbedder:
    def __init__(self):
        self.model_name = EMBEDDING_CONFIG["MODEL_NAME"]
        self.model_type = EMBEDDING_CONFIG["MODEL_TYPE"]
        self.batch_size = EMBEDDING_CONFIG["BATCH_SIZE"]
        self.device = EMBEDDING_CONFIG["DEVICE"]
        self.max_length = EMBEDDING_CONFIG["MAX_LENGTH"]
        self.medical_model_enabled = EMBEDDING_CONFIG["MEDICAL_MODEL"]["ENABLED"]
        self.medical_model_path = EMBEDDING_CONFIG["MEDICAL_MODEL"]["MODEL_PATH"]
        
        # 加载模型
        self.model = self.load_model()
    
    def load_model(self):
        """加载嵌入模型"""
        try:
            if self.medical_model_enabled and os.path.exists(self.medical_model_path):
                # 使用医疗领域微调模型
                print(f"加载医疗领域微调模型: {self.medical_model_path}")
                model = SentenceTransformer(self.medical_model_path, device=self.device)
            else:
                # 使用通用模型
                print(f"加载通用嵌入模型: {self.model_name}")
                model = SentenceTransformer(self.model_name, device=self.device)
            
            # 设置最大长度
            if hasattr(model, 'max_seq_length'):
                model.max_seq_length = self.max_length
            
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def embed_text(self, text):
        """将单个文本嵌入为向量"""
        try:
            # 确保文本是字符串
            if not isinstance(text, str):
                text = str(text)
            
            # 处理空文本
            if not text.strip():
                return None
            
            # 嵌入
            embedding = self.model.encode(
                text,
                batch_size=self.batch_size,
                show_progress_bar=False,
                convert_to_tensor=False
            )
            
            return embedding.tolist()
        except Exception as e:
            print(f"Error embedding text: {e}")
            return None
    
    def embed_chunks(self, chunks):
        """将多个文本块嵌入为向量"""
        embedded_chunks = []
        
        # 批量处理
        texts = []
        chunk_indices = []
        
        for i, chunk in enumerate(chunks):
            text = chunk.get('content', '')
            if text:
                texts.append(text)
                chunk_indices.append(i)
        
        if texts:
            try:
                # 批量嵌入
                embeddings = self.model.encode(
                    texts,
                    batch_size=self.batch_size,
                    show_progress_bar=False,
                    convert_to_tensor=False
                )
                
                # 将嵌入向量添加到块中
                for i, idx in enumerate(chunk_indices):
                    chunk = chunks[idx].copy()
                    chunk['embedding'] = embeddings[i].tolist()
                    embedded_chunks.append(chunk)
            except Exception as e:
                print(f"Error embedding chunks: {e}")
                # 回退到单个处理
                for chunk in chunks:
                    text = chunk.get('content', '')
                    if text:
                        embedding = self.embed_text(text)
                        if embedding:
                            chunk_copy = chunk.copy()
                            chunk_copy['embedding'] = embedding
                            embedded_chunks.append(chunk_copy)
        
        return embedded_chunks
    
    def embed_query(self, query):
        """将查询文本嵌入为向量"""
        return self.embed_text(query)
    
    def get_embedding_dimension(self):
        """获取嵌入维度"""
        # 嵌入一个示例文本以获取维度
        sample_embedding = self.embed_text("示例文本")
        if sample_embedding:
            return len(sample_embedding)
        else:
            return EMBEDDING_CONFIG["EMBEDDING_DIM"]

if __name__ == "__main__":
    # 示例使用
    embedder = MedicalEmbedder()
    
    # 嵌入单个文本
    text = "糖尿病是一种慢性疾病，当胰腺不能产生足够的胰岛素或人体不能有效利用所产生的胰岛素时发生。"
    embedding = embedder.embed_text(text)
    print(f"单个文本嵌入维度: {len(embedding) if embedding else 0}")
    
    # 嵌入多个文本块
    sample_chunks = [
        {
            "id": "1",
            "content": "糖尿病的常见症状包括：多尿、口渴、多食、体重减轻、疲劳、视力模糊、伤口愈合缓慢、反复感染等。",
            "metadata": {"section": "症状"}
        },
        {
            "id": "2",
            "content": "糖尿病的治疗包括：饮食控制、运动疗法、药物治疗、血糖监测等。",
            "metadata": {"section": "治疗"}
        }
    ]
    
    embedded_chunks = embedder.embed_chunks(sample_chunks)
    print(f"嵌入的块数量: {len(embedded_chunks)}")
    for i, chunk in enumerate(embedded_chunks):
        print(f"块 {i+1} 嵌入维度: {len(chunk['embedding'])}")
    
    # 嵌入查询
    query = "糖尿病有哪些症状？"
    query_embedding = embedder.embed_query(query)
    print(f"查询嵌入维度: {len(query_embedding) if query_embedding else 0}")
