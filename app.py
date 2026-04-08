from flask import Flask, render_template, request, jsonify, send_file
import requests
import json
import io
from datetime import datetime
from config import get_config

# 读取配置
config = get_config()

app = Flask(__name__)

DASHSCOPE_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

SYSTEM_PROMPT = """你是一位资深的软件开发工程师，擅长从代码提交日志中提炼工作成果并生成专业的日报。

请根据用户提供的代码提交日志，生成一份结构清晰、专业的工作日报。

要求：
1. 按工作类别分类（如：功能开发、Bug修复、代码优化、文档更新等）
2. 每项工作用一句话概括，突出价值和成果，不要罗列具体代码细节
3. 包含今日工作总结和明日工作建议
4. 使用Markdown格式输出
5. 语言简洁专业，适合向上级汇报

输出格式示例：
## 工作日报 - 2024年xx月xx日

### 一、功能开发
- 完成了xxx功能的设计与开发，实现了xxx效果

### 二、Bug修复
- 修复了xxx问题，提升了系统稳定性

### 三、其他工作
- xxx

### 四、今日总结
今日主要完成了...

### 五、明日计划
1. xxx
2. xxx
"""


@app.route('/')
def index():
    return render_template('index.html', default_model=config['model'])


@app.route('/generate', methods=['POST'])
def generate_report():
    data = request.json
    commit_logs = data.get('commit_logs', '').strip()
    api_key = data.get('api_key', '').strip() or config['api_key']
    model = data.get('model', '').strip() or config['model']
    
    if not commit_logs:
        return jsonify({'error': '请输入代码提交日志'}), 400
    
    if not api_key:
        return jsonify({
            'error': '未配置 API Key',
            'detail': '请在 config.ini 中配置 api_key，或在页面上输入'
        }), 400
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        payload = {
            'model': model,
            'input': {
                'messages': [
                    {'role': 'system', 'content': SYSTEM_PROMPT},
                    {'role': 'user', 'content': f'请根据以下代码提交日志生成日报：\n\n{commit_logs}'}
                ]
            },
            'parameters': {
                'result_format': 'message',
                'max_tokens': 2000
            }
        }
        
        response = requests.post(
            DASHSCOPE_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            error_data = response.json()
            error_msg = error_data.get('message', '未知错误')
            if 'Invalid API-key' in error_msg:
                return jsonify({
                    'error': 'API Key 无效',
                    'detail': '请检查你的通义千问 API Key 是否正确'
                }), 401
            return jsonify({'error': f'API调用失败: {error_msg}'}), 500
        
        result = response.json()
        report_content = result['output']['choices'][0]['message']['content']
        
        return jsonify({
            'success': True,
            'report': report_content
        })
        
    except requests.exceptions.Timeout:
        return jsonify({'error': '请求超时，请稍后重试'}), 500
    except Exception as e:
        return jsonify({'error': f'生成失败: {str(e)}'}), 500


@app.route('/config', methods=['GET'])
def get_config_status():
    """获取配置状态（不包含敏感信息）"""
    return jsonify({
        'has_api_key': bool(config['api_key']),
        'default_model': config['model']
    })


@app.route('/download', methods=['POST'])
def download_report():
    data = request.json
    content = data.get('content', '')
    
    if not content:
        return jsonify({'error': '内容为空'}), 400
    
    # 生成文件名
    today = datetime.now().strftime('%Y%m%d')
    filename = f'日报_{today}.md'
    
    # 创建内存文件
    file_io = io.BytesIO(content.encode('utf-8'))
    file_io.seek(0)
    
    return send_file(
        file_io,
        mimetype='text/markdown',
        as_attachment=True,
        download_name=filename
    )


if __name__ == '__main__':
    app.run(
        debug=config['debug'],
        host=config['host'],
        port=config['port']
    )
