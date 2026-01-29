# PDF解析器

import os
import json
from unstructured.partition.pdf import partition_pdf
from unstructured.staging.base import elements_to_json
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
            
            # 使用unstructured解析PDF
            elements = partition_pdf(
                filename=pdf_path,
                strategy="hi_res",
                extract_images_in_pdf=False,
                infer_table_structure=True,
                chunking_strategy="by_title",
                max_characters=4000,
                new_after_n_chars=3800,
                combine_text_under_n_chars=2000
            )
            
            # 转换为JSON格式
            elements_json = elements_to_json(elements)
            
            # 提取元数据和内容
            parsed_data = self.extract_metadata_and_content(elements_json, pdf_path, source_name)
            
            # 保存解析结果
            self.save_parsed_result(parsed_data, pdf_path, source_name)
            
            return parsed_data
        except Exception as e:
            print(f"Error parsing PDF {pdf_path}: {e}")
            return None
    
    def extract_metadata_and_content(self, elements_json, pdf_path, source_name):
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
        
        # 提取标题（通常是第一个大标题）
        for element in elements_json:
            if element["type"] == "Title" and element["text"]:
                parsed_data["metadata"]["title"] = element["text"]
                break
        
        # 提取内容
        current_section = {
            "type": "text",
            "content": "",
            "section": ""
        }
        
        for element in elements_json:
            if element["type"] == "Title":
                # 保存当前section
                if current_section["content"]:
                    parsed_data["content"].append(current_section)
                
                # 开始新section
                current_section = {
                    "type": "text",
                    "content": "",
                    "section": element["text"]
                }
            elif element["type"] == "Text":
                current_section["content"] += element["text"] + "\n"
            elif element["type"] == "Table":
                # 保存表格
                parsed_data["tables"].append({
                    "content": element["text"],
                    "section": current_section["section"]
                })
        
        # 保存最后一个section
        if current_section["content"]:
            parsed_data["content"].append(current_section)
        
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
