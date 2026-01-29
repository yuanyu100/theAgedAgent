# 数据源白名单配置

# 学术库（需处理版权与访问权限）
ACADEMIC_SOURCES = {
    "万方医学": {
        "url": "https://www.wanfangdata.com.cn/",
        "allowed_domains": ["wanfangdata.com.cn"],
        "url_patterns": ["/paper.*", "/periodical.*"]
    },
    "CNKI": {
        "url": "https://www.cnki.net/",
        "allowed_domains": ["cnki.net"],
        "url_patterns": ["/kcms/detail.*", "/gb/periodical.*"]
    },
    "PubMed": {
        "url": "https://pubmed.ncbi.nlm.nih.gov/",
        "allowed_domains": ["pubmed.ncbi.nlm.nih.gov"],
        "url_patterns": [r"/\d+/.*"]
    },
    "Google Scholar": {
        "url": "https://scholar.google.com/",
        "allowed_domains": ["scholar.google.com"],
        "url_patterns": ["/scholar?q=.*"]
    }
}

# 权威机构
AUTHORITY_SOURCES = {
    "WHO": {
        "url": "https://www.who.int/",
        "allowed_domains": ["who.int"],
        "url_patterns": ["/news-room.*", "/publications.*"]
    },
    "中国CDC": {
        "url": "https://www.chinacdc.cn/",
        "allowed_domains": ["chinacdc.cn"],
        "url_patterns": ["/zh-cn/tzgg.*", "/zh-cn/jkzt.*"]
    },
    "中华医学会": {
        "url": "https://www.cma.org.cn/",
        "allowed_domains": ["cma.org.cn"],
        "url_patterns": ["/yxgw.*", "/zlzn.*"]
    }
}

# 权威科普
POPULAR_SCIENCE_SOURCES = {
    "丁香医生": {
        "url": "https://dxy.com/",
        "allowed_domains": ["dxy.com"],
        "url_patterns": ["/article.*", "/topic.*"]
    },
    "北京协和医院": {
        "url": "https://www.pumch.cn/",
        "allowed_domains": ["pumch.cn"],
        "url_patterns": ["/kepu.*", "/health.*"]
    },
    "上海瑞金医院": {
        "url": "https://www.rjh.com.cn/",
        "allowed_domains": ["rjh.com.cn"],
        "url_patterns": ["/kepu.*", "/health.*"]
    }
}

# MVP阶段数据源（限定范围）
MVP_SOURCES = {
    **AUTHORITY_SOURCES,
    **POPULAR_SCIENCE_SOURCES
}

# 所有数据源
ALL_SOURCES = {
    **ACADEMIC_SOURCES,
    **AUTHORITY_SOURCES,
    **POPULAR_SCIENCE_SOURCES
}

# 疾病类型配置（MVP阶段）
MVP_DISEASES = [
    "高血压",
    "糖尿病"
]
