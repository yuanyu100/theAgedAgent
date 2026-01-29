# 风格转化模块

class StyleTransfer:
    def __init__(self):
        # 医学术语到通俗语言的映射
        self.medical_terms = {
            # 症状
            "高血压": "血压高",
            "糖尿病": "血糖高",
            "冠心病": "心脏冠状动脉疾病",
            "脑卒中": "中风",
            "心梗": "心肌梗死",
            "脑梗": "脑梗死",
            "肺炎": "肺部感染",
            "胃炎": "胃部炎症",
            "肠炎": "肠道炎症",
            "肝炎": "肝脏炎症",
            "肾炎": "肾脏炎症",
            "关节炎": "关节炎症",
            "哮喘": "气喘",
            "过敏": "过敏性反应",
            
            # 检查
            "血常规": "血液常规检查",
            "尿常规": "尿液常规检查",
            "肝功能": "肝脏功能检查",
            "肾功能": "肾脏功能检查",
            "心电图": "心脏电活动检查",
            "B超": "超声波检查",
            "CT": "计算机断层扫描",
            "MRI": "核磁共振检查",
            "X光": "X射线检查",
            
            # 治疗
            "ACEI类药物": "血管紧张素转换酶抑制剂类药物",
            "ARB类药物": "血管紧张素受体拮抗剂类药物",
            "降糖药": "降低血糖的药物",
            "降压药": "降低血压的药物",
            "降脂药": "降低血脂的药物",
            "胰岛素": "调节血糖的激素",
            "化疗": "化学药物治疗",
            "放疗": "放射线治疗",
            
            # 其他医学术语
            "高血糖症": "血糖升高",
            "低血糖症": "血糖降低",
            "高脂血症": "血脂升高",
            "高血压危象": "血压突然急剧升高",
            "糖尿病酮症酸中毒": "糖尿病严重并发症，血液中酮体过多",
            "胰岛素抵抗": "身体对胰岛素的反应减弱",
            "糖耐量受损": "血糖调节能力下降",
            "肾功能不全": "肾脏功能减弱",
            "肝功能不全": "肝脏功能减弱",
            "心功能不全": "心脏功能减弱"
        }
        
        # 复杂句型到通俗表达的映射
        self.complex_sentences = {
            r"[A-Za-z]+类药物可引起.*": "您吃的这个药，有可能会让{symptom}，这是正常反应之一。",
            r"[A-Za-z]+类药物适用于.*": "这个药适合{condition}的患者使用。",
            r"建议患者.*": "建议您{action}。",
            r"患者应避免.*": "您应该避免{action}。",
            r"研究表明.*": "根据研究，{finding}。",
            r"临床试验显示.*": "临床试验显示，{result}。"
        }
    
    def transfer(self, text):
        """将专业医学语言转化为通俗语言"""
        if not text:
            return text
        
        # 替换医学术语
        for term, replacement in self.medical_terms.items():
            text = text.replace(term, replacement)
        
        # 替换复杂句型
        import re
        for pattern, replacement in self.complex_sentences.items():
            matches = re.findall(pattern, text)
            for match in matches:
                # 提取症状、条件等信息
                if "可引起" in match:
                    symptom = match.split("可引起")[1].strip()
                    text = text.replace(match, replacement.format(symptom=symptom))
                elif "适用于" in match:
                    condition = match.split("适用于")[1].strip()
                    text = text.replace(match, replacement.format(condition=condition))
                elif "建议患者" in match:
                    action = match.split("建议患者")[1].strip()
                    text = text.replace(match, replacement.format(action=action))
                elif "患者应避免" in match:
                    action = match.split("患者应避免")[1].strip()
                    text = text.replace(match, replacement.format(action=action))
                elif "研究表明" in match:
                    finding = match.split("研究表明")[1].strip()
                    text = text.replace(match, replacement.format(finding=finding))
                elif "临床试验显示" in match:
                    result = match.split("临床试验显示")[1].strip()
                    text = text.replace(match, replacement.format(result=result))
        
        # 调整语气，使其更亲切
        text = self.adjust_tone(text)
        
        return text
    
    def adjust_tone(self, text):
        """调整语气，使其更亲切"""
        # 添加亲切的开头
        friendly_openings = ["您知道吗？", "跟您说一下，", "告诉您一个小知识，", "您可以了解一下，"]
        
        # 调整结尾
        friendly_endings = ["，您明白了吗？", "，希望对您有帮助！", "，您可以参考一下。", "，祝您健康！"]
        
        # 随机选择一个开头和结尾
        import random
        if random.random() > 0.5:
            opening = random.choice(friendly_openings)
            text = opening + text
        
        if random.random() > 0.5:
            ending = random.choice(friendly_endings)
            text = text + ending
        
        # 替换生硬的表达
        tone_adjustments = {
            "必须": "建议",
            "应该": "建议您",
            "需要": "建议您",
            "禁止": "最好不要",
            "请勿": "最好不要",
            "注意": "请您注意",
            "警告": "提醒您"
        }
        
        for 生硬表达, 亲切表达 in tone_adjustments.items():
            text = text.replace(生硬表达, 亲切表达)
        
        return text
    
    def transfer_batch(self, texts):
        """批量转化文本风格"""
        return [self.transfer(text) for text in texts]

if __name__ == "__main__":
    style_transfer = StyleTransfer()
    
    # 测试示例
    test_texts = [
        "ACEI类药物可引起干咳，这是常见的副作用之一。",
        "糖尿病患者应避免高糖饮食，建议适量运动。",
        "研究表明，定期监测血糖有助于控制糖尿病。",
        "高血压患者应定期测量血压，遵医嘱服药。"
    ]
    
    print("原始文本:")
    for text in test_texts:
        print(f"- {text}")
    
    print("\n转化后:")
    for text in test_texts:
        transferred = style_transfer.transfer(text)
        print(f"- {transferred}")
