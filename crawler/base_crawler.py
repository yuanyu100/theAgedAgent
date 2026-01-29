# 基础爬虫类

import os
import re
import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from config.data_sources import MVP_SOURCES
from config.crawler_config import CRAWLER_CONFIG, STORAGE_CONFIG, URL_FILTER_CONFIG, BROWSER_CONFIG

class BaseCrawler:
    def __init__(self):
        self.sources = MVP_SOURCES
        self.download_delay = CRAWLER_CONFIG["DOWNLOAD_DELAY"]
        self.headers = {
            "User-Agent": random.choice(BROWSER_CONFIG["USER_AGENTS"]),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 创建存储目录
        for path_key in STORAGE_CONFIG.values():
            os.makedirs(path_key, exist_ok=True)
    
    def is_valid_url(self, url, source_domain):
        """验证URL是否有效"""
        # 检查域名
        parsed_url = urlparse(url)
        if parsed_url.netloc not in source_domain:
            return False
        
        # 检查排除模式
        for pattern in URL_FILTER_CONFIG["EXCLUDE_PATTERNS"]:
            if re.search(pattern, url):
                return False
        
        # 检查包含模式（MVP阶段）
        if URL_FILTER_CONFIG["INCLUDE_PATTERNS"]:
            for pattern in URL_FILTER_CONFIG["INCLUDE_PATTERNS"]:
                if re.search(pattern, url):
                    break
            else:
                return False
        
        return True
    
    def get_html(self, url, retry=0):
        """获取网页HTML"""
        try:
            time.sleep(self.download_delay)
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            if retry < CRAWLER_CONFIG["RETRY_TIMES"]:
                print(f"Error getting {url}: {e}, retrying...")
                return self.get_html(url, retry + 1)
            else:
                print(f"Failed to get {url} after {CRAWLER_CONFIG['RETRY_TIMES']} retries")
                return None
    
    def get_pdf(self, url, save_path):
        """下载PDF文件"""
        try:
            time.sleep(self.download_delay)
            response = self.session.get(url, timeout=60, stream=True)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        except Exception as e:
            print(f"Error downloading PDF {url}: {e}")
            return False
    
    def extract_links(self, html, base_url, allowed_domains):
        """从HTML中提取链接"""
        soup = BeautifulSoup(html, 'lxml')
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            
            if self.is_valid_url(full_url, allowed_domains):
                links.append(full_url)
        
        return list(set(links))  # 去重
    
    def crawl_source(self, source_name, source_config):
        """爬取单个数据源"""
        print(f"开始爬取数据源: {source_name}")
        base_url = source_config["url"]
        allowed_domains = source_config["allowed_domains"]
        
        # 获取首页
        html = self.get_html(base_url)
        if not html:
            return
        
        # 提取链接
        links = self.extract_links(html, base_url, allowed_domains)
        print(f"找到 {len(links)} 个链接")
        
        # 爬取每个链接
        for link in links[:10]:  # MVP阶段限制数量
            print(f"爬取: {link}")
            page_html = self.get_html(link)
            if page_html:
                # 保存HTML
                self.save_html(link, page_html, source_name)
                
                # 检查是否有PDF链接
                self.extract_and_download_pdfs(page_html, link, source_name)
    
    def save_html(self, url, html, source_name):
        """保存HTML文件"""
        filename = re.sub(r'[^a-zA-Z0-9_]', '_', urlparse(url).path.strip('/')) or 'index'
        filename = f"{filename}.html"
        save_path = os.path.join(STORAGE_CONFIG["HTML_STORE_PATH"], source_name)
        os.makedirs(save_path, exist_ok=True)
        
        with open(os.path.join(save_path, filename), 'w', encoding='utf-8') as f:
            f.write(html)
    
    def extract_and_download_pdfs(self, html, base_url, source_name):
        """提取并下载PDF链接"""
        soup = BeautifulSoup(html, 'lxml')
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href.endswith('.pdf'):
                pdf_url = urljoin(base_url, href)
                filename = os.path.basename(urlparse(pdf_url).path)
                save_path = os.path.join(STORAGE_CONFIG["PDF_STORE_PATH"], source_name)
                os.makedirs(save_path, exist_ok=True)
                
                print(f"下载PDF: {pdf_url}")
                self.get_pdf(pdf_url, os.path.join(save_path, filename))
    
    def run(self):
        """运行爬虫"""
        for source_name, source_config in self.sources.items():
            self.crawl_source(source_name, source_config)

if __name__ == "__main__":
    crawler = BaseCrawler()
    crawler.run()
