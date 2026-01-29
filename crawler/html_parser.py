# HTML解析器

import os
import json
import re
from bs4 import BeautifulSoup
from config.crawler_config import STORAGE_CONFIG

class HTMLParser:
    def __init__(self):
        self.html_store_path = STORAGE_CONFIG["HTML_STORE_PATH"]
        self.parsed_store_path = STORAGE_CONFIG["PARSED_STORE_PATH"]
        os.makedirs(self.parsed_store_path, exist_ok=True)
    
    def parse_html(self, html_path, source_name):
        """解析HTML文件"""
        try:
            print(f"开始解析HTML: {html_path}")
            
            # 读取HTML文件
            with open(html_path, 'r', encoding='utf-8') as f:
                html = f.read()
            
            # 清洗HTML
            cleaned_html = self.clean_html(html)
            
            # 提取元数据和内容
            parsed_data = self.extract_metadata_and_content(cleaned_html, html_path, source_name)
            
            # 保存解析结果
            self.save_parsed_result(parsed_data, html_path, source_name)
            
            return parsed_data
        except Exception as e:
            print(f"Error parsing HTML {html_path}: {e}")
            return None
    
    def clean_html(self, html):
        """清洗HTML，去除广告、导航栏等"""
        soup = BeautifulSoup(html, 'lxml')
        
        # 移除脚本和样式
        for script in soup(['script', 'style']):
            script.decompose()
        
        # 移除广告
        for ad in soup.select('[class*=ad], [class*=advertisement], [id*=ad], [id*=advertisement]'):
            try:
                ad.decompose()
            except:
                pass
        
        # 移除导航栏
        for nav in soup.select('nav, [class*=nav], [id*=nav]'):
            try:
                nav.decompose()
            except:
                pass
        
        # 移除页脚
        for footer in soup.select('footer, [class*=footer], [id*=footer]'):
            try:
                footer.decompose()
            except:
                pass
        
        # 移除侧边栏
        for sidebar in soup.select('[class*=sidebar], [id*=sidebar], aside'):
            try:
                sidebar.decompose()
            except:
                pass
        
        return soup
    
    def extract_metadata_and_content(self, soup, html_path, source_name):
        """提取元数据和内容"""
        parsed_data = {
            "source": source_name,
            "file_path": html_path,
            "filename": os.path.basename(html_path),
            "metadata": {
                "title": "",
                "authors": [],
                "publication_date": "",
                "source_organization": source_name
            },
            "content": [],
            "url": ""
        }
        
        # 提取标题
        title = soup.find('title')
        if title:
            parsed_data["metadata"]["title"] = title.get_text(strip=True)
        
        # 尝试从meta标签提取信息
        meta_title = soup.find('meta', {'name': 'title'})
        if meta_title and meta_title.get('content'):
            parsed_data["metadata"]["title"] = meta_title.get('content')
        
        # 提取发布日期
        date_patterns = [
            r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?',
            r'\d{4}[-/年]\d{1,2}[-/月]',
            r'\d{4}年',
            r'\d{4}-\d{2}-\d{2}'
        ]
        
        text = soup.get_text()
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                parsed_data["metadata"]["publication_date"] = match.group(0)
                break
        
        # 提取作者
        author_patterns = [
            r'作者[:：]\s*([^\n]+)',
            r'作者\s*([^\n]+)',
            r'by\s*([^\n]+)',
            r'Written by\s*([^\n]+)'
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, text)
            if match:
                authors = match.group(1).split('、')
                parsed_data["metadata"]["authors"] = [author.strip() for author in authors]
                break
        
        # 提取正文内容
        content_tags = ['article', 'main', 'div[class*=content]', 'div[id*=content]', 'section[class*=content]', 'section[id*=content]']
        content = ""
        
        for tag in content_tags:
            elements = soup.select(tag)
            if elements:
                for element in elements:
                    content += element.get_text(separator='\n', strip=True) + "\n"
                break
        
        # 如果没有找到特定的内容标签，使用body
        if not content:
            body = soup.find('body')
            if body:
                content = body.get_text(separator='\n', strip=True)
        
        # 清理内容
        content = re.sub(r'\s+', ' ', content).strip()
        
        # 分段
        paragraphs = re.split(r'[。！？]\s*', content)
        sections = []
        current_section = {"type": "text", "content": "", "section": "正文"}
        
        for paragraph in paragraphs:
            if paragraph:
                current_section["content"] += paragraph + "。"
                if len(current_section["content"]) > 500:
                    sections.append(current_section)
                    current_section = {"type": "text", "content": "", "section": "正文"}
        
        if current_section["content"]:
            sections.append(current_section)
        
        parsed_data["content"] = sections
        
        return parsed_data
    
    def save_parsed_result(self, parsed_data, html_path, source_name):
        """保存解析结果"""
        if not parsed_data:
            return
        
        # 创建源目录
        source_parsed_path = os.path.join(self.parsed_store_path, source_name)
        os.makedirs(source_parsed_path, exist_ok=True)
        
        # 生成文件名
        filename = os.path.basename(html_path).replace('.html', '.json')
        save_path = os.path.join(source_parsed_path, filename)
        
        # 保存为JSON
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)
        
        print(f"解析结果保存到: {save_path}")
    
    def parse_all_htmls(self):
        """解析所有HTML文件"""
        for source_name in os.listdir(self.html_store_path):
            source_html_path = os.path.join(self.html_store_path, source_name)
            if not os.path.isdir(source_html_path):
                continue
            
            print(f"开始解析 {source_name} 的HTML文件")
            
            for html_file in os.listdir(source_html_path):
                if html_file.endswith('.html'):
                    html_path = os.path.join(source_html_path, html_file)
                    self.parse_html(html_path, source_name)

if __name__ == "__main__":
    parser = HTMLParser()
    parser.parse_all_htmls()
