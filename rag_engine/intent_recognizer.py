# 意图识别模块

import re
from config.model_config import RAG_CONFIG

class IntentRecognizer:
    def __init__(self):
        self.enabled = RAG_CONFIG["INTENT_RECOGNITION"]["ENABLED"]
        self.threshold = RAG_CONFIG["INTENT_RECOGNITION"]["THRESHOLD"]
        self.intent_types = RAG_CONFIG["INTENT_RECOGNITION"]["INTENT_TYPES"]
        
        # 意图关键词配置
        self.intent_keywords = {
            "medical_consultation": [
                # 症状描述
                "头晕", "头痛", "恶心", "呕吐", "发热", "咳嗽", "腹痛", "腹泻", "便秘",
                "乏力", "疲劳", "失眠", "多梦", "口渴", "多尿", "多食", "体重减轻",
                "视力模糊", "伤口愈合缓慢", "反复感染", "胸痛", "心悸", "呼吸困难",
                "血压", "血糖", "血脂", "胆固醇",
                
                # 疾病名称
                "高血压", "糖尿病", "冠心病", "脑卒中", "心梗", "脑梗", "肺炎", "胃炎",
                "肠炎", "肝炎", "肾炎", "关节炎", "哮喘", "过敏", "癌症", "肿瘤",
                
                # 治疗相关
                "吃药", "用药", "服药", "剂量", "副作用", "禁忌", "注意事项",
                "治疗", "手术", "化疗", "放疗", "康复", "锻炼", "运动",
                
                # 检查相关
                "检查", "化验", "体检", "血常规", "尿常规", "肝功能", "肾功能",
                "心电图", "B超", "CT", "MRI", "X光",
                
                # 饮食相关
                "饮食", "食谱", "营养", "忌口", "能吃", "不能吃", "推荐",
                
                # 咨询用语
                "怎么办", "怎么治", "如何", "为什么", "原因", "预防", "保健",
                "建议", "意见", "指导", "帮助"
            ],
            "chat": [
                "你好", "您好", "早上好", "下午好", "晚上好", "再见", "拜拜",
                "谢谢", "谢谢", "不客气", "没关系", "好的", "知道了", "明白",
                "今天", "天气", "吃饭", "睡觉", "工作", "学习", "生活",
                "高兴", "开心", "难过", "伤心", "生气", "愤怒"
            ],
            "greeting": [
                "你好", "您好", "早上好", "下午好", "晚上好", "初次见面", "认识你"
            ]
        }
        
        # 医疗相关正则表达式
        self.medical_patterns = [
            r'\d+血压', r'血压\d+',
            r'\d+血糖', r'血糖\d+',
            r'\d+度', r'发烧',
            r'吃.*药', r'喝.*药',
            r'怎么.*治', r'如何.*治',
            r'.*病.*怎么办', r'.*症状.*怎么办'
        ]
    
    def recognize_intent(self, text):
        """识别用户意图"""
        if not self.enabled:
            return {"intent": "medical_consultation", "confidence": 1.0}
        
        if not text or not isinstance(text, str):
            return {"intent": "chat", "confidence": 0.5}
        
        # 计算各意图的得分
        scores = {}
        for intent in self.intent_types:
            scores[intent] = self.calculate_intent_score(text, intent)
        
        # 确定最高得分的意图
        max_intent = max(scores, key=scores.get)
        max_score = scores[max_intent]
        
        # 特殊处理：对于明确的问候语和闲聊语句，即使得分低于阈值，也识别为chat或greeting
        if max_intent in ["chat", "greeting"] and max_score > 0:
            return {"intent": max_intent, "confidence": max_score}
        
        # 应用阈值
        if max_score < self.threshold:
            # 如果得分低于阈值，默认为医疗咨询
            return {"intent": "medical_consultation", "confidence": max_score}
        
        return {"intent": max_intent, "confidence": max_score}
    
    def calculate_intent_score(self, text, intent):
        """计算文本与特定意图的匹配得分"""
        score = 0.0
        keywords = self.intent_keywords.get(intent, [])
        
        # 关键词匹配
        matched_count = 0
        for keyword in keywords:
            if keyword in text:
                matched_count += 1
                score += 1.0
        
        # 正则表达式匹配（仅医疗咨询）
        if intent == "medical_consultation":
            for pattern in self.medical_patterns:
                if re.search(pattern, text):
                    score += 1.5
        
        # 计算得分
        if intent == "medical_consultation":
            # 对于医疗咨询，每匹配一个关键词得0.3分
            score = min(0.3 * matched_count, 1.0)
        elif intent in ["chat", "greeting"]:
            # 对于问候和闲聊
            if matched_count > 0:
                # 检查是否包含医疗关键词
                has_medical_keywords = False
                for med_keyword in self.intent_keywords.get("medical_consultation", []):
                    if med_keyword in text:
                        has_medical_keywords = True
                        break
                
                if has_medical_keywords:
                    # 如果包含医疗关键词，大幅降低聊天得分
                    score = 0.2
                else:
                    # 纯聊天或问候
                    score = 0.8
            else:
                score = 0.0
        
        return score
    
    def is_medical_consultation(self, text):
        """判断是否为医疗咨询"""
        intent_result = self.recognize_intent(text)
        return intent_result["intent"] == "medical_consultation"
    
    def is_chat(self, text):
        """判断是否为闲聊"""
        intent_result = self.recognize_intent(text)
        return intent_result["intent"] == "chat"
    
    def is_greeting(self, text):
        """判断是否为问候"""
        intent_result = self.recognize_intent(text)
        return intent_result["intent"] == "greeting"

if __name__ == "__main__":
    # 示例使用
    recognizer = IntentRecognizer()
    
    test_texts = [
        "你好，我最近总是头晕，怎么办？",
        "高血压患者能吃什么水果？",
        "糖尿病患者的饮食建议有哪些？",
        "你好，今天天气怎么样？",
        "谢谢医生的建议",
        "我最近血压有点高，140/90，需要吃药吗？"
    ]
    
    for text in test_texts:
        result = recognizer.recognize_intent(text)
        print(f"文本: {text}")
        print(f"意图: {result['intent']}, 置信度: {result['confidence']:.2f}")
        print()
