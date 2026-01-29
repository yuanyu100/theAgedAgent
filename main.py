#!/usr/bin/env python3
# 主入口文件

import os
import sys
import argparse
from config.data_sources import MVP_SOURCES
from crawler.scheduler import CrawlerScheduler
from knowledge_base.etl import ETLPipeline
from knowledge_base.chunker import MedicalChunker
from knowledge_base.embedder import MedicalEmbedder
from knowledge_base.vector_db import VectorDatabase
from ui.web_ui import WebUI
from utils.security import SecurityManager

class SilverGuardAI:
    def __init__(self):
        self.security_manager = SecurityManager()
    
    def run_crawler(self):
        """运行爬虫"""
        print("启动爬虫模块...")
        scheduler = CrawlerScheduler()
        scheduler.run()
    
    def build_knowledge_base(self):
        """构建知识库"""
        print("构建知识库...")
        
        # 运行ETL
        etl = ETLPipeline()
        processed_data = etl.run()
        
        if not processed_data:
            print("没有处理数据，知识库构建失败")
            return
        
        # 分块
        chunker = MedicalChunker()
        chunks = []
        for document in processed_data:
            document_chunks = chunker.chunk_document(document)
            chunks.extend(document_chunks)
        
        print(f"生成了 {len(chunks)} 个文本块")
        
        # 向量化
        embedder = MedicalEmbedder()
        embedded_chunks = embedder.embed_chunks(chunks)
        
        print(f"成功嵌入 {len(embedded_chunks)} 个文本块")
        
        # 存入向量数据库
        vector_db = VectorDatabase()
        added_count = vector_db.add_chunks(embedded_chunks)
        
        print(f"成功添加 {added_count} 个文本块到向量数据库")
        print("知识库构建完成")
    
    def run_web_ui(self, host='0.0.0.0', port=5000, debug=False):
        """运行Web界面"""
        print(f"启动Web界面，地址: http://{host}:{port}")
        web_ui = WebUI()
        web_ui.run(host=host, port=port, debug=debug)
    
    def run(self, mode, **kwargs):
        """运行模式"""
        if mode == "crawler":
            self.run_crawler()
        elif mode == "build_kb":
            self.build_knowledge_base()
        elif mode == "web":
            host = kwargs.get('host', '0.0.0.0')
            port = kwargs.get('port', 5000)
            debug = kwargs.get('debug', False)
            self.run_web_ui(host=host, port=port, debug=debug)
        else:
            print(f"未知模式: {mode}")
            self.show_help()
    
    def show_help(self):
        """显示帮助信息"""
        print("银龄康护助手 (SilverGuard AI) - 慢性病知识问答版")
        print("Usage: python main.py [mode] [options]")
        print("\n模式:")
        print("  crawler     - 运行爬虫模块，采集医疗数据")
        print("  build_kb    - 构建知识库，处理数据并入库")
        print("  web         - 运行Web界面，提供健康咨询服务")
        print("\n选项:")
        print("  --host      - Web服务器主机地址 (默认: 0.0.0.0)")
        print("  --port      - Web服务器端口 (默认: 5000)")
        print("  --debug     - 启用调试模式")
        print("\n示例:")
        print("  python main.py crawler")
        print("  python main.py build_kb")
        print("  python main.py web --host 127.0.0.1 --port 8080 --debug")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="银龄康护助手 (SilverGuard AI) - 慢性病知识问答版")
    parser.add_argument('mode', choices=['crawler', 'build_kb', 'web'], help='运行模式')
    parser.add_argument('--host', default='0.0.0.0', help='Web服务器主机地址')
    parser.add_argument('--port', type=int, default=5000, help='Web服务器端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    try:
        # 创建SilverGuardAI实例
        silverguard = SilverGuardAI()
        
        # 运行指定模式
        silverguard.run(
            mode=args.mode,
            host=args.host,
            port=args.port,
            debug=args.debug
        )
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
