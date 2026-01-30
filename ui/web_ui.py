# Web界面模块

import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from rag_engine.intent_recognizer import IntentRecognizer
from rag_engine.retriever import MultiRetriever
from rag_engine.generator import AnswerGenerator
from config.model_config import SAFETY_CONFIG

class WebUI:
    def __init__(self):
        import os
        # 获取当前文件目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 创建templates目录路径
        template_dir = os.path.join(current_dir, 'templates')
        # 确保templates目录存在
        os.makedirs(template_dir, exist_ok=True)
        # 创建默认模板
        self.create_default_template(template_dir)
        
        # 初始化Flask应用，指定模板目录
        self.app = Flask(__name__, template_folder=template_dir)
        CORS(self.app)
        self.setup_routes()
        
        # 初始化模块
        self.intent_recognizer = IntentRecognizer()
        self.retriever = MultiRetriever()
        self.generator = AnswerGenerator()
        
        # 免责声明
        self.disclaimer = SAFETY_CONFIG["DISCLAIMER"]
    
    def handle_chat(self, query):
        """处理闲聊"""
        chat_responses = {
            '你好': '您好！我是银龄康护助手，很高兴为您服务。请问您有什么健康问题需要咨询？',
            '您好': '您好！我是银龄康护助手，很高兴为您服务。请问您有什么健康问题需要咨询？',
            '早上好': '早上好！我是银龄康护助手，很高兴为您服务。请问您有什么健康问题需要咨询？',
            '下午好': '下午好！我是银龄康护助手，很高兴为您服务。请问您有什么健康问题需要咨询？',
            '晚上好': '晚上好！我是银龄康护助手，很高兴为您服务。请问您有什么健康问题需要咨询？',
            '谢谢': '不客气！如果您还有其他健康问题，随时可以咨询我。',
            '谢谢': '不客气！如果您还有其他健康问题，随时可以咨询我。',
            '再见': '再见！祝您健康愉快！',
            '拜拜': '再见！祝您健康愉快！'
        }
        
        for key, value in chat_responses.items():
            if key in query:
                return value
        
        return '您好！我是银龄康护助手，专注于为您提供权威的健康咨询服务。请问您有什么健康问题需要咨询？'
    
    def setup_routes(self):
        """设置路由"""
        @self.app.route('/')
        def index():
            return render_template('index.html', disclaimer=self.disclaimer)
        
        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            try:
                data = request.json
                query = data.get('query', '').strip()
                
                if not query:
                    return jsonify({
                        'status': 'error',
                        'message': '请输入您的问题'
                    })
                
                # 识别意图
                intent_result = self.intent_recognizer.recognize_intent(query)
                
                if intent_result['intent'] == 'chat' or intent_result['intent'] == 'greeting':
                    # 闲聊或问候
                    return jsonify({
                        'status': 'success',
                        'answer': self.handle_chat(query),
                        'citations': [],
                        'intent': intent_result['intent']
                    })
                else:
                    # 医疗咨询
                    # 检索相关信息
                    retrieved_results = self.retriever.retrieve(query)
                    
                    # 生成回答
                    answer_result = self.generator.generate(query, retrieved_results)
                    
                    return jsonify({
                        'status': 'success',
                        'answer': answer_result.get('answer', ''),
                        'citations': answer_result.get('citations', []),
                        'confidence': answer_result.get('confidence', 0.0),
                        'warning': answer_result.get('warning', ''),
                        'intent': intent_result['intent']
                    })
            except Exception as e:
                print(f"Error in chat endpoint: {e}")
                return jsonify({
                    'status': 'error',
                    'message': '处理请求时发生错误，请稍后重试'
                })
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """运行Web服务器"""
        self.app.run(host=host, port=port, debug=debug)
    
    def create_default_template(self, template_dir):
        """创建默认的HTML模板"""
        index_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>银龄康护助手</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: "Microsoft YaHei", Arial, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background-color: #4CAF50;
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .disclaimer {
            background-color: #fff3cd;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 1.1em;
            border: 1px solid #ffeeba;
        }
        
        .chat-container {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .chat-messages {
            height: 500px;
            overflow-y: auto;
            padding: 20px;
            background-color: #f9f9f9;
        }
        
        .message {
            margin-bottom: 20px;
            max-width: 80%;
        }
        
        .user-message {
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 10px 10px 0 10px;
            align-self: flex-end;
            margin-left: auto;
        }
        
        .bot-message {
            background-color: white;
            padding: 15px;
            border-radius: 10px 10px 10px 0;
            border: 1px solid #e0e0e0;
        }
        
        .message-content {
            font-size: 1.2em;
            line-height: 1.5;
        }
        
        .citations {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #e0e0e0;
            font-size: 0.9em;
            color: #666;
        }
        
        .input-container {
            display: flex;
            padding: 20px;
            border-top: 1px solid #e0e0e0;
        }
        
        .input-box {
            flex: 1;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 25px;
            font-size: 1.2em;
            resize: none;
        }
        
        .send-button {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            margin-left: 10px;
            font-size: 1.2em;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .send-button:hover {
            background-color: #45a049;
        }
        
        .voice-button {
            background-color: #2196F3;
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            margin-left: 10px;
            font-size: 1.2em;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .voice-button:hover {
            background-color: #0b7dda;
        }
        
        .voice-button.recording {
            background-color: #f44336;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% {
                box-shadow: 0 0 0 0 rgba(244, 67, 54, 0.7);
            }
            70% {
                box-shadow: 0 0 0 10px rgba(244, 67, 54, 0);
            }
            100% {
                box-shadow: 0 0 0 0 rgba(244, 67, 54, 0);
            }
        }
        
        /* 响应式设计 */
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .chat-messages {
                height: 400px;
            }
            
            .message {
                max-width: 90%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>银龄康护助手</h1>
            <p>专业、权威的健康咨询服务</p>
        </div>
        
        <div class="disclaimer">
            {{ disclaimer }}
        </div>
        
        <div class="chat-container">
            <div class="chat-messages" id="chat-messages">
                <div class="message bot-message">
                    <div class="message-content">
                        您好！我是银龄康护助手，很高兴为您服务。请问您有什么健康问题需要咨询？
                    </div>
                </div>
            </div>
            
            <div class="input-container">
                <textarea class="input-box" id="input-box" placeholder="请输入您的问题..."></textarea>
                <button class="voice-button" id="voice-button" title="语音输入">🎤</button>
                <button class="send-button" id="send-button" title="发送">📤</button>
            </div>
        </div>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const chatMessages = document.getElementById('chat-messages');
            const inputBox = document.getElementById('input-box');
            const sendButton = document.getElementById('send-button');
            const voiceButton = document.getElementById('voice-button');
            
            // 发送消息
            function sendMessage() {
                const query = inputBox.value.trim();
                if (!query) return;
                
                // 添加用户消息
                addMessage(query, 'user');
                inputBox.value = '';
                
                // 显示正在输入
                const typingId = addMessage('正在为您查询...', 'bot', true);
                
                // 发送请求
                fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ query: query })
                })
                .then(response => response.json())
                .then(data => {
                    // 移除正在输入
                    document.getElementById(typingId).remove();
                    
                    if (data.status === 'success') {
                        // 添加机器人回答
                        addMessage(data.answer, 'bot', false, data.citations);
                    } else {
                        // 添加错误消息
                        addMessage(data.message || '处理请求时发生错误', 'bot');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById(typingId).remove();
                    addMessage('网络错误，请稍后重试', 'bot');
                });
            }
            
            // 添加消息
            function addMessage(content, type, isTyping = false, citations = []) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}-message`;
                
                if (isTyping) {
                    messageDiv.id = 'typing-' + Date.now();
                }
                
                const contentDiv = document.createElement('div');
                contentDiv.className = 'message-content';
                contentDiv.innerHTML = content;
                
                messageDiv.appendChild(contentDiv);
                
                // 添加引用
                if (citations && citations.length > 0) {
                    const citationsDiv = document.createElement('div');
                    citationsDiv.className = 'citations';
                    citationsDiv.innerHTML = '<strong>参考资料：</strong><br>';
                    
                    citations.forEach(cite => {
                        const citeItem = document.createElement('div');
                        citeItem.textContent = `[${cite.number}] ${cite.source} - ${cite.document_title || '未命名文档'} (${cite.publication_date || '未知日期'})`;
                        citationsDiv.appendChild(citeItem);
                    });
                    
                    messageDiv.appendChild(citationsDiv);
                }
                
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
                
                return messageDiv.id;
            }
            
            // 发送按钮点击事件
            sendButton.addEventListener('click', sendMessage);
            
            // 回车键发送
            inputBox.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
            
            // 语音输入
            let recognition = null;
            
            voiceButton.addEventListener('click', function() {
                if ('webkitSpeechRecognition' in window) {
                    if (recognition && recognition.recognizing) {
                        // 停止录音
                        recognition.stop();
                        return;
                    }
                    
                    // 开始录音
                    recognition = new webkitSpeechRecognition();
                    recognition.continuous = false;
                    recognition.interimResults = false;
                    recognition.lang = 'zh-CN';
                    
                    voiceButton.classList.add('recording');
                    voiceButton.title = '停止录音';
                    
                    recognition.onstart = function() {
                        console.log('语音识别开始');
                    };
                    
                    recognition.onresult = function(event) {
                        const transcript = event.results[0][0].transcript;
                        inputBox.value = transcript;
                        sendMessage();
                    };
                    
                    recognition.onerror = function(event) {
                        console.error('语音识别错误:', event.error);
                        alert('语音识别失败，请重试');
                    };
                    
                    recognition.onend = function() {
                        voiceButton.classList.remove('recording');
                        voiceButton.title = '语音输入';
                        recognition.recognizing = false;
                    };
                    
                    recognition.recognizing = true;
                    recognition.start();
                } else {
                    alert('您的浏览器不支持语音输入功能');
                }
            });
        });
    </script>
</body>
</html>
'''
        
        with open(os.path.join(template_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(index_html)

if __name__ == "__main__":
    web_ui = WebUI()
    web_ui.run(debug=True)
