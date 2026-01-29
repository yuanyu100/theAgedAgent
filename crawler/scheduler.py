# 定时任务调度器

import os
import time
import schedule
from datetime import datetime
from config.crawler_config import SCHEDULER_CONFIG
from .base_crawler import BaseCrawler
from .pdf_parser import PDFParser
from .html_parser import HTMLParser

class CrawlerScheduler:
    def __init__(self):
        self.base_crawler = BaseCrawler()
        self.pdf_parser = PDFParser()
        self.html_parser = HTMLParser()
        self.scheduler = schedule
    
    def run_incremental_crawl(self):
        """执行增量爬取"""
        print(f"[{datetime.now()}] 开始增量爬取")
        
        # 爬取数据源
        for source_name, source_config in self.base_crawler.sources.items():
            self.base_crawler.crawl_source(source_name, source_config)
        
        # 解析新下载的文件
        self.parse_new_files()
        
        print(f"[{datetime.now()}] 增量爬取完成")
    
    def run_full_crawl(self):
        """执行全量爬取"""
        print(f"[{datetime.now()}] 开始全量爬取")
        
        # 爬取所有数据源
        for source_name, source_config in self.base_crawler.sources.items():
            self.base_crawler.crawl_source(source_name, source_config)
        
        # 解析所有文件
        self.parse_all_files()
        
        print(f"[{datetime.now()}] 全量爬取完成")
    
    def parse_new_files(self):
        """解析新下载的文件"""
        print("开始解析新文件")
        
        # 解析PDF文件
        self.parse_new_pdfs()
        
        # 解析HTML文件
        self.parse_new_htmls()
        
        print("新文件解析完成")
    
    def parse_all_files(self):
        """解析所有文件"""
        print("开始解析所有文件")
        
        # 解析所有PDF文件
        self.pdf_parser.parse_all_pdfs()
        
        # 解析所有HTML文件
        self.html_parser.parse_all_htmls()
        
        print("所有文件解析完成")
    
    def parse_new_pdfs(self):
        """解析新的PDF文件"""
        from config.crawler_config import STORAGE_CONFIG
        
        pdf_store_path = STORAGE_CONFIG["PDF_STORE_PATH"]
        parsed_store_path = STORAGE_CONFIG["PARSED_STORE_PATH"]
        
        for source_name in os.listdir(pdf_store_path):
            source_pdf_path = os.path.join(pdf_store_path, source_name)
            if not os.path.isdir(source_pdf_path):
                continue
            
            source_parsed_path = os.path.join(parsed_store_path, source_name)
            os.makedirs(source_parsed_path, exist_ok=True)
            
            # 获取已解析的文件列表
            parsed_files = set()
            for file in os.listdir(source_parsed_path):
                if file.endswith('.json'):
                    parsed_files.add(file.replace('.json', '.pdf'))
            
            # 解析未解析的PDF文件
            for pdf_file in os.listdir(source_pdf_path):
                if pdf_file.endswith('.pdf') and pdf_file not in parsed_files:
                    pdf_path = os.path.join(source_pdf_path, pdf_file)
                    self.pdf_parser.parse_pdf(pdf_path, source_name)
    
    def parse_new_htmls(self):
        """解析新的HTML文件"""
        from config.crawler_config import STORAGE_CONFIG
        
        html_store_path = STORAGE_CONFIG["HTML_STORE_PATH"]
        parsed_store_path = STORAGE_CONFIG["PARSED_STORE_PATH"]
        
        for source_name in os.listdir(html_store_path):
            source_html_path = os.path.join(html_store_path, source_name)
            if not os.path.isdir(source_html_path):
                continue
            
            source_parsed_path = os.path.join(parsed_store_path, source_name)
            os.makedirs(source_parsed_path, exist_ok=True)
            
            # 获取已解析的文件列表
            parsed_files = set()
            for file in os.listdir(source_parsed_path):
                if file.endswith('.json'):
                    parsed_files.add(file.replace('.json', '.html'))
            
            # 解析未解析的HTML文件
            for html_file in os.listdir(source_html_path):
                if html_file.endswith('.html') and html_file not in parsed_files:
                    html_path = os.path.join(source_html_path, html_file)
                    self.html_parser.parse_html(html_path, source_name)
    
    def schedule_tasks(self):
        """调度定时任务"""
        # 增量爬取任务
        incremental_interval = SCHEDULER_CONFIG["INCREMENTAL_CRAWL_INTERVAL"]
        if incremental_interval.days == 1:
            self.scheduler.every().day.at("02:00").do(self.run_incremental_crawl)
        elif incremental_interval.days == 7:
            self.scheduler.every().week.at("02:00").do(self.run_incremental_crawl)
        
        # 全量爬取任务
        full_interval = SCHEDULER_CONFIG["FULL_CRAWL_INTERVAL"]
        if full_interval.days == 7:
            self.scheduler.every().week.at("01:00").do(self.run_full_crawl)
        elif full_interval.days == 28:
            self.scheduler.every(4).weeks.at("01:00").do(self.run_full_crawl)
        
        print("定时任务已调度")
    
    def run(self):
        """运行调度器"""
        # 调度任务
        self.schedule_tasks()
        
        # 立即执行一次增量爬取
        self.run_incremental_crawl()
        
        # 持续运行
        print("调度器开始运行，按Ctrl+C退出")
        while True:
            self.scheduler.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    scheduler = CrawlerScheduler()
    scheduler.run()
