# 回答生成模块

import os
import openai
from config.model_config import LLM_CONFIG, RAG_CONFIG, SAFETY_CONFIG
from rag_engine.citation import CitationManager

class AnswerGenerator:
    def __init__(self):
        self.model_name = LLM_CONFIG["MODEL_NAME"]
        self.api_key = os.environ.get("OPENAI_API_KEY", LLM_CONFIG["API_KEY"])
        self.temperature = LLM_CONFIG["TEMPERATURE"]
        self.max_tokens = LLM_CONFIG["MAX_TOKENS"]
        self.system_prompt = LLM_CONFIG["SYSTEM_PROMPT"]
        self.style_transfer_enabled = RAG_CONFIG["STYLE_TRANSFER"]["ENABLED"]
        self.target_style = RAG_CONFIG["STYLE_TRANSFER"]["TARGET_STYLE"]
        self.hallucination_suppression = SAFETY_CONFIG["HALLUCINATION_SUPPRESSION"]["ENABLED"]
        self.unknown_response = SAFETY_CONFIG["HALLUCINATION_SUPPRESSION"]["UNKNOWN_RESPONSE"]
        self.context_coverage_threshold = SAFETY_CONFIG["HALLUCINATION_SUPPRESSION"]["CONTEXT_COVERAGE_THRESHOLD"]
        
        # 初始化引用管理器
        self.citation_manager = CitationManager()
        
        # 配置OpenAI
        if self.api_key and not self.api_key.startswith("$"):
            openai.api_key = self.api_key
    
    def generate(self, query, retrieved_results):
        """生成回答"""
        # 检查上下文覆盖度
        if self.hallucination_suppression:
            coverage = self.calculate_context_coverage(query, retrieved_results)
            if coverage < self.context_coverage_threshold:
                return {
                    "answer": self.unknown_response,
                    "citations": [],
                    "confidence": 0.0,
                    "warning": "知识库中没有足够的相关信息"
                }
        
        # 构建提示
        prompt = self.build_prompt(query, retrieved_results)
        
        # 生成回答
        try:
            response = self.call_llm(prompt)
            
            # 处理回答
            answer = self.process_answer(response, retrieved_results)
            
            return answer
        except Exception as e:
            print(f"Error generating answer: {e}")
            return {
                "answer": self.unknown_response,
                "citations": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    def calculate_context_coverage(self, query, retrieved_results):
        """计算上下文覆盖度"""
        if not retrieved_results:
            return 0.0
        
        # 简单实现：基于检索结果的数量和得分
        total_score = sum([result.get("fused_score", result.get("score", 0)) for result in retrieved_results])
        avg_score = total_score / len(retrieved_results) if retrieved_results else 0
        
        # 覆盖度 = 平均得分 * (检索结果数量 / 期望数量)
        expected_count = 3
        count_factor = min(len(retrieved_results) / expected_count, 1.0)
        
        coverage = avg_score * count_factor
        return coverage
    
    def build_prompt(self, query, retrieved_results):
        """构建提示"""
        # 系统提示
        system_prompt = self.system_prompt
        
        # 添加风格转化指令
        if self.style_transfer_enabled:
            system_prompt += f"\n\n{self.target_style}"
        
        # 构建上下文
        context = "根据以下权威医疗信息回答用户问题：\n\n"
        
        for i, result in enumerate(retrieved_results, 1):
            content = result["content"]
            metadata = result["metadata"]
            
            # 构建引用信息
            source_info = f"来源: {metadata.get('source', '')}"
            if metadata.get('document_title'):
                source_info += f", 标题: {metadata.get('document_title')}"
            if metadata.get('publication_date'):
                source_info += f", 发布日期: {metadata.get('publication_date')}"
            if metadata.get('authors'):
                authors = ", ".join(metadata.get('authors'))
                source_info += f", 作者: {authors}"
            
            context += f"[{i}] {content}\n\n{source_info}\n\n"
        
        # 用户问题
        user_prompt = f"用户问题: {query}\n\n请基于上述信息回答问题，确保每条医疗建议都有来源支持，并在回答中使用[1][2]这样的角标标注来源。"
        
        return {
            "system": system_prompt,
            "user": user_prompt
        }
    
    def call_llm(self, prompt):
        """调用LLM"""
        # 这里使用OpenAI API作为示例
        # 实际应用中可以替换为其他LLM
        
        try:
            if self.api_key and not self.api_key.startswith("$"):
                response = openai.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": prompt["system"]},
                        {"role": "user", "content": prompt["user"]}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                return response.choices[0].message.content
            else:
                # 模拟回答（用于开发测试）
                return self.generate_mock_answer(prompt["user"])
        except Exception as e:
            print(f"Error calling LLM: {e}")
            raise
    
    def generate_mock_answer(self, user_prompt):
        """生成模拟回答（用于开发测试）"""
        mock_answers = {
            "糖尿病有哪些症状？": "糖尿病的常见症状包括：多尿、口渴、多食、体重减轻、疲劳、视力模糊、伤口愈合缓慢、反复感染等[1]。如果您出现这些症状，应及时就医[2]。",
            "高血压患者能吃什么水果？": "高血压患者可以适量食用苹果、香蕉、橙子、猕猴桃等富含钾元素的水果[1]。这些水果有助于降低血压[2]。",
            "糖尿病患者的饮食建议有哪些？": "糖尿病患者的饮食建议包括：控制总热量、合理分配碳水化合物、增加膳食纤维摄入、选择低GI食物、规律进餐等[1][2]。"
        }
        
        for key, value in mock_answers.items():
            if key in user_prompt:
                return value
        
        return "根据权威医疗信息，您的问题需要更详细的分析。建议您咨询专业医生获取个性化建议。"
    
    def process_answer(self, answer, retrieved_results):
        """处理回答"""
        # 提取引用
        citations = self.citation_manager.extract_citations(answer, retrieved_results)
        
        # 计算置信度
        confidence = self.calculate_confidence(retrieved_results)
        
        return {
            "answer": answer,
            "citations": citations,
            "confidence": confidence
        }
    
    def calculate_confidence(self, retrieved_results):
        """计算回答置信度"""
        if not retrieved_results:
            return 0.0
        
        # 基于检索结果的平均得分
        total_score = sum([result.get("fused_score", result.get("score", 0)) for result in retrieved_results])
        avg_score = total_score / len(retrieved_results) if retrieved_results else 0
        
        return avg_score

if __name__ == "__main__":
    # 示例使用
    generator = AnswerGenerator()
    
    # 示例检索结果
    sample_results = [
        {
            "id": "1",
            "content": "糖尿病的常见症状包括：多尿、口渴、多食、体重减轻、疲劳、视力模糊、伤口愈合缓慢、反复感染等。",
            "score": 0.9,
            "metadata": {
                "source": "WHO",
                "document_title": "糖尿病防治指南",
                "publication_date": "2022",
                "authors": ["WHO Expert Group"]
            }
        },
        {
            "id": "2",
            "content": "如果出现糖尿病相关症状，应及时就医进行诊断和治疗。",
            "score": 0.85,
            "metadata": {
                "source": "中国CDC",
                "document_title": "糖尿病预防与控制",
                "publication_date": "2021",
                "authors": ["中国CDC专家"]
            }
        }
    ]
    
    # 测试查询
    query = "糖尿病有哪些症状？"
    result = generator.generate(query, sample_results)
    
    print(f"查询: {query}")
    print(f"回答: {result['answer']}")
    print(f"引用: {result['citations']}")
    print(f"置信度: {result['confidence']:.2f}")
