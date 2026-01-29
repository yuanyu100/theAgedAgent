# 银龄康护助手 (SilverGuard AI) 实现计划

## 项目结构
```
silverguard-ai/
├── config/           # 配置文件
│   ├── data_sources.py  # 数据源白名单配置
│   ├── crawler_config.py # 爬虫配置
│   └── model_config.py   # 模型配置
├── crawler/          # 爬虫模块
│   ├── __init__.py
│   ├── base_crawler.py   # 基础爬虫类
│   ├── pdf_parser.py     # PDF解析器
│   ├── html_parser.py    # HTML解析器
│   └── scheduler.py      # 定时任务调度
├── knowledge_base/   # 知识库模块
│   ├── __init__.py
│   ├── etl.py            # 数据处理管道
│   ├── chunker.py        # 文本分块器
│   ├── embedder.py       # 向量化器
│   └── vector_db.py      # 向量数据库操作
├── rag_engine/        # RAG引擎
│   ├── __init__.py
│   ├── intent_recognizer.py  # 意图识别
│   ├── retriever.py     # 多路召回
│   ├── generator.py     # 回答生成
│   └── citation.py      # 引用溯源
├── ui/                # 用户界面
│   ├── __init__.py
│   ├── web_ui.py        # Web界面
│   ├── asr_tts.py       # 语音交互
│   └── style_transfer.py # 风格转化
├── utils/             # 工具函数
│   ├── __init__.py
│   ├── text_utils.py    # 文本处理工具
│   ├── security.py      # 安全与合规
│   └── logging.py       # 日志管理
├── main.py            # 主入口
├── requirements.txt   # 依赖项
└── README.md          # 项目说明
```

## 实现步骤

### 1. 环境搭建与依赖配置
- 创建Python虚拟环境
- 安装必要依赖：爬虫库、PDF解析库、向量数据库客户端、LLM SDK等

### 2. 配置模块实现
- 数据源白名单配置：定义权威医疗网站列表
- 爬虫配置：设置爬取规则、频率、存储路径
- 模型配置：配置Embedding模型和LLM参数

### 3. 爬虫模块实现
- 基础爬虫类：支持定向采集、URL过滤
- PDF解析器：使用MinerU或Unstructured解析医疗论文
- HTML解析器：清洗网页内容，提取正文和元数据
- 定时调度器：实现增量爬取

### 4. 知识库模块实现
- 数据处理管道：清洗、去重、格式化
- 语义分块器：按医疗文档语义结构切分
- 向量化器：使用医疗领域微调模型
- 向量数据库：实现数据存储和检索

### 5. RAG引擎实现
- 意图识别：区分闲聊和医疗咨询
- 多路召回：结合BM25和向量搜索
- 回答生成：基于检索结果生成医疗建议
- 引用溯源：为每句建议添加来源标注

### 6. 用户界面实现
- Web界面：老年适老化设计，大字体、简洁布局
- 语音交互：集成ASR/TTS服务
- 风格转化：将专业医学术语转化为通俗易懂的语言

### 7. 安全与合规
- 免责声明：在界面显著位置显示
- 幻觉抑制：检测知识库覆盖度，未知问题返回"不清楚"
- 敏感词过滤：过滤违禁内容

### 8. 测试与优化
- 功能测试：验证爬虫、RAG、UI各模块
- 性能测试：优化响应速度
- 准确率评估：测试医疗建议的准确性

## 技术选型
- **爬虫**：Scrapy + Selenium (处理动态内容)
- **PDF解析**：Unstructured (支持复杂排版)
- **向量数据库**：Chroma (轻量级，适合MVP)
- **Embedding模型**：BGE-M3 (支持中文)
- **LLM**：GPT-4o-mini (平衡成本和性能)
- **Web框架**：Flask (快速开发)
- **语音交互**：百度语音API (支持方言)

## MVP阶段范围
- 仅支持高血压和糖尿病两个病种
- 数据源限定为WHO、CDC、中华医学会指南、丁香医生
- 实现文字输入/输出，基本引用标注
- 简化版Web界面，无语音交互

## 后续迭代
- 扩展病种覆盖
- 增加语音交互功能
- 优化PDF解析能力
- 引入用户健康档案管理