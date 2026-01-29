# 数据处理管道 (ETL)

import os
import json
import re
from config.crawler_config import STORAGE_CONFIG
from config.data_sources import MVP_DISEASES

class ETLPipeline:
    def __init__(self):
        self.parsed_store_path = STORAGE_CONFIG["PARSED_STORE_PATH"]
        self.processed_data = []
    
    def extract(self):
        """提取解析后的数据"""
        extracted_data = []
        
        # 遍历所有数据源目录
        for source_name in os.listdir(self.parsed_store_path):
            source_path = os.path.join(self.parsed_store_path, source_name)
            if not os.path.isdir(source_path):
                continue
            
            # 遍历所有解析文件
            for file_name in os.listdir(source_path):
                if file_name.endswith('.json'):
                    file_path = os.path.join(source_path, file_name)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        extracted_data.append(data)
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")
        
        return extracted_data
    
    def transform(self, data):
        """转换数据"""
        transformed_data = []
        
        for item in data:
            # 清洗数据
            cleaned_item = self.clean_data(item)
            
            # 过滤相关疾病
            if self.is_relevant_to_disease(cleaned_item):
                transformed_data.append(cleaned_item)
        
        return transformed_data
    
    def clean_data(self, item):
        """清洗数据"""
        cleaned_item = item.copy()
        
        # 清洗标题
        if cleaned_item.get('metadata', {}).get('title'):
            cleaned_item['metadata']['title'] = self.clean_text(cleaned_item['metadata']['title'])
        
        # 清洗内容
        if cleaned_item.get('content'):
            cleaned_content = []
            for section in cleaned_item['content']:
                if section.get('content'):
                    section['content'] = self.clean_text(section['content'])
                    cleaned_content.append(section)
            cleaned_item['content'] = cleaned_content
        
        # 清洗表格
        if cleaned_item.get('tables'):
            cleaned_tables = []
            for table in cleaned_item['tables']:
                if table.get('content'):
                    table['content'] = self.clean_text(table['content'])
                    cleaned_tables.append(table)
            cleaned_item['tables'] = cleaned_tables
        
        return cleaned_item
    
    def clean_text(self, text):
        """清洗文本"""
        # 去除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 去除首尾空白
        text = text.strip()
        # 去除特殊字符
        text = re.sub(r'[\x00-\x1f\x7f]', '', text)
        return text
    
    def is_relevant_to_disease(self, item):
        """判断是否与目标疾病相关"""
        # 检查标题
        title = item.get('metadata', {}).get('title', '')
        if any(disease in title for disease in MVP_DISEASES):
            return True
        
        # 检查内容
        content = ' '.join([section.get('content', '') for section in item.get('content', [])])
        if any(disease in content for disease in MVP_DISEASES):
            return True
        
        # 检查表格
        tables = ' '.join([table.get('content', '') for table in item.get('tables', [])])
        if any(disease in tables for disease in MVP_DISEASES):
            return True
        
        return False
    
    def load(self, data, output_path=None):
        """加载数据"""
        if output_path:
            # 保存处理后的数据
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.processed_data = data
        return data
    
    def run(self, output_path=None):
        """运行ETL流程"""
        print("开始ETL流程")
        
        # 提取
        print("提取数据...")
        extracted_data = self.extract()
        print(f"提取了 {len(extracted_data)} 条数据")
        
        # 转换
        print("转换数据...")
        transformed_data = self.transform(extracted_data)
        print(f"转换后剩余 {len(transformed_data)} 条数据")
        
        # 加载
        print("加载数据...")
        loaded_data = self.load(transformed_data, output_path)
        print(f"加载完成，共 {len(loaded_data)} 条数据")
        
        return loaded_data

if __name__ == "__main__":
    etl = ETLPipeline()
    output_path = os.path.join(STORAGE_CONFIG["DATA_STORE_PATH"], "processed", "medical_data.json")
    etl.run(output_path)
