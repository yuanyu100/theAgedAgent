# 模型配置

# Embedding模型配置
EMBEDDING_CONFIG = {
    # 模型名称
    "MODEL_NAME": "BAAI/bge-m3",
    # 模型类型
    "MODEL_TYPE": "sentence-transformer",
    # 嵌入维度
    "EMBEDDING_DIM": 1024,
    # 批处理大小
    "BATCH_SIZE": 32,
    # 设备
    "DEVICE": "cpu",
    # 文本长度限制
    "MAX_LENGTH": 512,
    # 中文医疗领域微调模型（可选）
    "MEDICAL_MODEL": {
        "ENABLED": False,
        "MODEL_PATH": "path/to/medical/embedding/model"
    }
}

# 向量数据库配置
VECTOR_DB_CONFIG = {
    # 数据库类型
    "DB_TYPE": "chromadb",
    # 存储路径
    "PERSIST_DIRECTORY": "./vector_db",
    # 集合名称
    "COLLECTION_NAME": "medical_knowledge",
    # 相似度阈值
    "SIMILARITY_THRESHOLD": 0.7,
    # 检索数量
    "TOP_K": 5,
    # 元数据过滤
    "METADATA_FILTERS": None
}

# LLM配置
LLM_CONFIG = {
    # 模型名称
    "MODEL_NAME": "inclusionAI/Ling-mini-2.0",
    # API提供商
    "API_PROVIDER": "openai",
    # API密钥
    "API_KEY": "sk-rejkwjvqwerqgfmolygzjxqqoaejovbkeieyuwxtogokvgqp",
    # API基础URL
    "BASE_URL": "https://api.siliconflow.cn/v1",
    # 温度参数
    "TEMPERATURE": 0.3,
    # Top P参数
    "TOP_P": 0.7,
    # 最大输出长度
    "MAX_TOKENS": 10000,
    # 超时时间（秒）
    "TIMEOUT": 600,
    # 思考模式
    "THINKING": "disabled",
    # 上下文窗口大小
    "CONTEXT_WINDOW": 16384,
    # 系统提示
    "SYSTEM_PROMPT": "你是银龄康护助手，一个基于循证医学的AI医疗顾问。请使用专业、易懂的语言回答用户的医疗问题，确保每一条医疗建议都有权威来源支持。回答要亲切、耐心，适合老年人理解。"
}

# RAG配置
RAG_CONFIG = {
    # 多路召回配置
    "MULTI_RETRIEVAL": {
        "ENABLED": True,
        "WEIGHTS": {
            "vector": 0.7,
            "bm25": 0.3
        }
    },
    # 引用溯源配置
    "CITATION": {
        "ENABLED": True,
        "FORMAT": "[{}]",
        "INCLUDE_URL": True,
        "INCLUDE_AUTHOR": True
    },
    # 风格转化配置
    "STYLE_TRANSFER": {
        "ENABLED": True,
        "TARGET_STYLE": "医生对患者说的大白话，亲切易懂，避免专业术语"
    },
    # 意图识别配置
    "INTENT_RECOGNITION": {
        "ENABLED": True,
        "THRESHOLD": 0.8,
        "INTENT_TYPES": ["medical_consultation", "chat", "greeting"]
    }
}

# 安全与合规配置
SAFETY_CONFIG = {
    # 免责声明
    "DISCLAIMER": "本服务仅供信息参考，不能替代医生面诊，急症请立即就医。",
    # 幻觉抑制
    "HALLUCINATION_SUPPRESSION": {
        "ENABLED": True,
        "UNKNOWN_RESPONSE": "抱歉，我没有找到相关的权威信息，建议您咨询专业医生。",
        "CONTEXT_COVERAGE_THRESHOLD": 0.6
    },
    # 敏感词过滤
    "SENSITIVE_FILTER": {
        "ENABLED": True,
        "FILTER_TYPES": ["prohibited_drugs", "feudal_superstition", "medical_misinformation"]
    }
}
