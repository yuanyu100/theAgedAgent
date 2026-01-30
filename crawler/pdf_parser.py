# PDF解析器

import os
import json
from pdfminer.high_level import extract_text
from config.crawler_config import STORAGE_CONFIG

class PDFParser:
    def __init__(self):
        self.pdf_store_path = STORAGE_CONFIG["PDF_STORE_PATH"]
        self.parsed_store_path = STORAGE_CONFIG["PARSED_STORE_PATH"]
        os.makedirs(self.parsed_store_path, exist_ok=True)
    
    def parse_pdf(self, pdf_path, source_name):
        """解析PDF文件"""
        try:
            print(f"开始解析PDF: {pdf_path}")
            
            # 使用pdfminer.six提取文本
            text = extract_text(pdf_path)
            
            # 提取元数据和内容
            parsed_data = self.extract_metadata_and_content(text, pdf_path, source_name)
            
            # 保存解析结果
            self.save_parsed_result(parsed_data, pdf_path, source_name)
            
            return parsed_data
        except Exception as e:
            print(f"Error parsing PDF {pdf_path}: {e}")
            return None
    
    def extract_metadata_and_content(self, text, pdf_path, source_name):
        """提取元数据和内容"""
        parsed_data = {
            "source": source_name,
            "file_path": pdf_path,
            "filename": os.path.basename(pdf_path),
            "metadata": {
                "title": "",
                "authors": [],
                "publication_date": "",
                "source_organization": source_name
            },
            "content": [],
            "tables": []
        }
        
        # 提取标题（使用前几行作为标题）
        lines = text.split('\n')
        title_lines = []
        for line in lines[:10]:  # 检查前10行
            line_stripped = line.strip()
            if line_stripped and len(line_stripped) > 10 and len(line_stripped) < 100:
                title_lines.append(line_stripped)
                if len(title_lines) >= 2:
                    break
        
        if title_lines:
            parsed_data["metadata"]["title"] = ' '.join(title_lines)
        else:
            # 如果没有找到合适的标题，使用文件名
            parsed_data["metadata"]["title"] = os.path.basename(pdf_path).replace('.pdf', '')
        
        # 提取内容（按段落分割）
        paragraphs = []
        current_paragraph = ""
        
        for line in lines:
            line_stripped = line.strip()
            if line_stripped:
                current_paragraph += line + "\n"
            else:
                if current_paragraph.strip():
                    paragraphs.append(current_paragraph.strip())
                    current_paragraph = ""
        
        if current_paragraph.strip():
            paragraphs.append(current_paragraph.strip())
        
        # 将段落组织为内容
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph) > 50:
                parsed_data["content"].append({
                    "type": "text",
                    "content": paragraph,
                    "section": f"Section {i+1}"
                })
        
        return parsed_data
    
    def save_parsed_result(self, parsed_data, pdf_path, source_name):
        """保存解析结果"""
        if not parsed_data:
            return
        
        # 创建源目录
        source_parsed_path = os.path.join(self.parsed_store_path, source_name)
        os.makedirs(source_parsed_path, exist_ok=True)
        
        # 生成文件名
        filename = os.path.basename(pdf_path).replace('.pdf', '.json')
        save_path = os.path.join(source_parsed_path, filename)
        
        # 保存为JSON
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)
        
        print(f"解析结果保存到: {save_path}")
    
    def parse_all_pdfs(self):
        """解析所有PDF文件"""
        for source_name in os.listdir(self.pdf_store_path):
            source_pdf_path = os.path.join(self.pdf_store_path, source_name)
            if not os.path.isdir(source_pdf_path):
                continue
            
            print(f"开始解析 {source_name} 的PDF文件")
            
            for pdf_file in os.listdir(source_pdf_path):
                if pdf_file.endswith('.pdf'):
                    pdf_path = os.path.join(source_pdf_path, pdf_file)
                    self.parse_pdf(pdf_path, source_name)

if __name__ == "__main__":
    parser = PDFParser()
    parser.parse_all_pdfs()
