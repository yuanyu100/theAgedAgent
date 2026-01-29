# 安全与合规模块

from config.model_config import SAFETY_CONFIG

class SecurityManager:
    def __init__(self):
        self.disclaimer = SAFETY_CONFIG["DISCLAIMER"]
        self.hallucination_suppression = SAFETY_CONFIG["HALLUCINATION_SUPPRESSION"]["ENABLED"]
        self.unknown_response = SAFETY_CONFIG["HALLUCINATION_SUPPRESSION"]["UNKNOWN_RESPONSE"]
        self.context_coverage_threshold = SAFETY_CONFIG["HALLUCINATION_SUPPRESSION"]["CONTEXT_COVERAGE_THRESHOLD"]
        self.sensitive_filter_enabled = SAFETY_CONFIG["SENSITIVE_FILTER"]["ENABLED"]
        self.filter_types = SAFETY_CONFIG["SENSITIVE_FILTER"]["FILTER_TYPES"]
        
        # 敏感词列表
        self.sensitive_words = {
            "prohibited_drugs": [
                "海洛因", "冰毒", "摇头丸", "K粉", "大麻", "可卡因", "鸦片", "吗啡",
                "杜冷丁", "芬太尼", "麻黄素", "安非他命", "迷幻药", "致幻剂"
            ],
            "feudal_superstition": [
                "算命", "风水", "占卜", "相面", "算卦", "驱鬼", "跳大神", "风水宝地",
                "生辰八字", "黄道吉日", "凶吉", "祸福", "因果报应", "前世今生", "轮回"
            ],
            "medical_misinformation": [
                "包治百病", "根治", "特效", "神奇", "秘方", "偏方", "祖传", "宫廷秘方",
                "永不复发", "100%有效", "无副作用", "纯天然", "无毒副作用", "神药", "仙丹"
            ]
        }
    
    def get_disclaimer(self):
        """获取免责声明"""
        return self.disclaimer
    
    def check_hallucination(self, query, retrieved_results):
        """检查幻觉风险"""
        if not self.hallucination_suppression:
            return False, ""
        
        # 计算上下文覆盖度
        coverage = self.calculate_context_coverage(query, retrieved_results)
        
        if coverage < self.context_coverage_threshold:
            return True, self.unknown_response
        
        return False, ""
    
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
    
    def filter_sensitive_content(self, text):
        """过滤敏感内容"""
        if not self.sensitive_filter_enabled:
            return text, []
        
        filtered_text = text
        detected_sensitive = []
        
        # 检查每种类型的敏感词
        for filter_type in self.filter_types:
            sensitive_words = self.sensitive_words.get(filter_type, [])
            for word in sensitive_words:
                if word in filtered_text:
                    # 替换敏感词
                    filtered_text = filtered_text.replace(word, "*" * len(word))
                    detected_sensitive.append({
                        "type": filter_type,
                        "word": word
                    })
        
        return filtered_text, detected_sensitive
    
    def validate_query(self, query):
        """验证查询是否合法"""
        # 检查敏感内容
        filtered_query, detected_sensitive = self.filter_sensitive_content(query)
        
        if detected_sensitive:
            return False, "您的查询包含敏感内容，请修改后重试", detected_sensitive
        
        # 检查查询长度
        if len(query) > 500:
            return False, "您的查询过长，请简洁表达您的问题", []
        
        # 检查空查询
        if not query or not query.strip():
            return False, "请输入您的问题", []
        
        return True, filtered_query, []
    
    def validate_answer(self, answer):
        """验证回答是否合法"""
        # 检查敏感内容
        filtered_answer, detected_sensitive = self.filter_sensitive_content(answer)
        
        if detected_sensitive:
            return False, "回答包含敏感内容", detected_sensitive
        
        # 检查回答长度
        if len(answer) > 2000:
            return False, "回答过长", []
        
        return True, filtered_answer, []

if __name__ == "__main__":
    security_manager = SecurityManager()
    
    # 测试免责声明
    print("免责声明:")
    print(security_manager.get_disclaimer())
    print()
    
    # 测试敏感词过滤
    test_text = "我听说海洛因可以治疗癌症，这是真的吗？"
    filtered_text, detected = security_manager.filter_sensitive_content(test_text)
    print("原始文本:", test_text)
    print("过滤后:", filtered_text)
    print("检测到的敏感内容:", detected)
    print()
    
    # 测试查询验证
    test_query = "算命的说我会得糖尿病，准吗？"
    valid, message, detected = security_manager.validate_query(test_query)
    print("测试查询:", test_query)
    print("验证结果:", valid)
    print("消息:", message)
    print("检测到的敏感内容:", detected)
