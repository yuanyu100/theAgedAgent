# 爬虫配置

import os
from datetime import timedelta

# 爬虫基础配置
CRAWLER_CONFIG = {
    # 爬取间隔（秒）
    "DOWNLOAD_DELAY": 5,
    # 并发请求数
    "CONCURRENT_REQUESTS": 4,
    # 自动限速
    "AUTOTHROTTLE_ENABLED": True,
    # 初始下载延迟
    "AUTOTHROTTLE_START_DELAY": 5,
    # 最大下载延迟
    "AUTOTHROTTLE_MAX_DELAY": 60,
    # 目标并发请求数
    "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
    # 重试次数
    "RETRY_TIMES": 3,
    # 允许的状态码
    "HTTPERROR_ALLOWED_CODES": [404, 403],
    # 日志级别
    "LOG_LEVEL": "INFO"
}

# 存储配置
STORAGE_CONFIG = {
    # 爬取数据存储路径
    "DATA_STORE_PATH": os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"),
    # PDF存储路径
    "PDF_STORE_PATH": os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "pdfs"),
    # HTML存储路径
    "HTML_STORE_PATH": os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "htmls"),
    # 解析结果存储路径
    "PARSED_STORE_PATH": os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "parsed")
}

# 定时任务配置
SCHEDULER_CONFIG = {
    # 增量爬取间隔
    "INCREMENTAL_CRAWL_INTERVAL": timedelta(days=1),
    # 全量爬取间隔
    "FULL_CRAWL_INTERVAL": timedelta(weeks=4),
    # 爬取时间窗口（避免高峰期）
    "CRAWL_TIME_WINDOW": {
        "start": "00:00",
        "end": "06:00"
    }
}

# URL过滤规则
URL_FILTER_CONFIG = {
    # 排除的URL模式
    "EXCLUDE_PATTERNS": [
        "*.js", "*.css", "*.jpg", "*.png", "*.gif", "*.svg",
        "*/login*", "*/register*", "*/logout*",
        "*/advertisement*", "*/promotion*", "*/sponsor*"
    ],
    # 包含的URL模式（仅对MVP阶段）
    "INCLUDE_PATTERNS": [
        "*高血压*", "*糖尿病*", "*hypertension*", "*diabetes*"
    ]
}

# 代理配置（可选）
PROXY_CONFIG = {
    "ENABLED": False,
    "HTTP_PROXY": "http://localhost:7890",
    "HTTPS_PROXY": "http://localhost:7890"
}

# 模拟浏览器配置
BROWSER_CONFIG = {
    "ENABLED": True,
    "HEADLESS": True,
    "USER_AGENTS": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/119.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0"
    ]
}
