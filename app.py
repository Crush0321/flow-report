"""
日报生成器 - Flask 后端服务
"""
from flask import Flask, render_template, request, jsonify, send_file
import requests
import json
import io
import os
import re
import configparser
from pathlib import Path
from datetime import datetime, timezone
from functools import wraps

app = Flask(__name__)

# 常量配置
CONFIG_FILE = Path(__file__).parent / 'config.ini'
DASHSCOPE_API_URL = os.getenv('DASHSCOPE_API_URL', 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation')
MAX_LOG_LENGTH = 10000
DEFAULT_MODEL = 'tongyi-xiaomi-analysis-pro'
DEFAULT_PORT = 5000
DEFAULT_HOST = '0.0.0.0'

# 提示词模板 - 正经模式
SYSTEM_PROMPT_TEMPLATE = """你是一位资深的软件开发工程师，擅长从代码提交日志中提炼工作成果并生成专业的日报。

请根据用户提供的代码提交日志，生成一份结构清晰、专业的工作日报。

要求：
1. 按工作类别分类（如：功能开发、Bug修复、代码优化、文档更新等）
2. 每项工作用一句话概括，突出价值和成果，不要罗列具体代码细节
3. 包含今日工作总结和明日工作建议
4. 使用Markdown格式输出
5. 语言简洁专业，适合向上级汇报

重要：今天是 {today}，日报标题必须准确使用这个日期。

输出格式示例：
## 工作日报 - {today}

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

# 提示词模板 - 摸鱼模式（幽默风趣、一本正经胡说八道）
MOYU_PROMPT_TEMPLATE = """你是一位"资深"的摸鱼大师，擅长把啥也没干的一天包装成忙碌充实的工作日。

请根据用户提供的代码提交日志（即使很少或很水），生成一份**看似专业、实则胡扯**的摸鱼日报。

**风格要求**：
1. **一本正经胡说八道** - 用专业的术语描述微不足道的事情
2. **夸张放大** - 把改个变量名说成"架构重构"，把看文档说成"技术预研"
3. **黑话满满** - 多用"赋能"、"抓手"、"闭环"、"底层逻辑"、"顶层设计"等互联网黑话
4. **避重就轻** - 没写代码就说"深入思考"、"方案设计"、"技术储备"
5. **假装忙碌** - 开会、喝水、上厕所都能包装成"跨部门协同"、"生理机能维护"

**重要**：今天是 {today}，日报标题必须用"摸鱼日报"或"工作日报（摸鱼版）

**输出格式**：
## 摸鱼日报 - {today}

### 一、深度技术钻研
- 对项目架构进行了深度思考，输出了3个思路（其实就在脑子里过了一下）

### 二、战略性休息
- 进行了长达2小时的眼部保健操（其实是闭目养神）

### 三、跨部门协同
- 积极参与了茶水间的非正式技术交流（和同事吹水）

### 四、今日总结
今日工作量饱满，在多个维度取得了突破性进展...

### 五、明日规划
1. 继续深入钻研技术方案
2. 优化个人工作流
"""

# 摸鱼关键词（用于自动检测）
MOYU_KEYWORDS = [
    '摸鱼', '划水', '休息', '睡觉', '躺平', '摆烂', '休息', '没干', '啥也没', 'water',
    'coffee', 'tea', 'lunch', 'dinner', 'break', 'fix typo', 'update readme',
    'merge', 'wip', 'work in progress'
]

# 摸鱼特征：提交数量少
MOYU_COMMIT_THRESHOLD = 3  # 少于3个提交可能是摸鱼


def get_today():
    """获取带时区的今日日期（中文格式）"""
    try:
        return datetime.now(timezone.utc).astimezone().strftime('%Y年%m月%d日')
    except Exception:
        # 降级方案
        return datetime.now().strftime('%Y年%m月%d日')


def safe_int(value, default=DEFAULT_PORT):
    """安全转换为整数"""
    if not value:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_bool(value, default=False):
    """安全转换为布尔值"""
    if not value:
        return default
    return str(value).lower() in ('true', '1', 'yes', 'on', 'enabled')


def get_config():
    """读取配置（优先级：环境变量 > config.ini > 默认值）"""
    # 读取 config.ini
    config_parser = configparser.ConfigParser()
    if CONFIG_FILE.exists():
        config_parser.read(CONFIG_FILE, encoding='utf-8')
    
    # 确保有必要的配置节
    if 'dashscope' not in config_parser:
        config_parser['dashscope'] = {}
    if 'flask' not in config_parser:
        config_parser['flask'] = {}
    
    dashscope_cfg = config_parser['dashscope']
    flask_cfg = config_parser['flask']
    
    # 优先级：环境变量 > config.ini > 默认值
    api_key = os.getenv('DASHSCOPE_API_KEY', '').strip() or dashscope_cfg.get('api_key', '').strip()
    model = os.getenv('DASHSCOPE_MODEL', '').strip() or dashscope_cfg.get('model', DEFAULT_MODEL).strip()
    
    return {
        'api_key': api_key,
        'model': model or DEFAULT_MODEL,
        'debug': safe_bool(os.getenv('FLASK_DEBUG')) or safe_bool(flask_cfg.get('debug')),
        'port': safe_int(os.getenv('FLASK_PORT')) or safe_int(flask_cfg.get('port'), DEFAULT_PORT),
        'host': os.getenv('FLASK_HOST', '').strip() or flask_cfg.get('host', DEFAULT_HOST).strip() or DEFAULT_HOST,
    }


def parse_api_error(response):
    """解析 API 错误响应，返回友好的错误信息"""
    try:
        data = response.json()
        error_code = data.get('code', 'Unknown')
        error_message = data.get('message', '未知错误')
        request_id = data.get('request_id', '')
        
        # 常见错误码映射
        error_map = {
            'InvalidApiKey': 'API Key 无效或已过期，请检查配置',
            'InsufficientBalance': '账户余额不足，请充值',
            'AccessDenied': '无权限访问该模型，请确认模型名称正确',
            'ModelNotFound': f'模型不存在: 当前使用的模型可能不可用，请更换模型后重试',
            'ContextLengthExceeded': '输入内容过长，请减少提交日志的长度',
            'RateLimitExceeded': '请求过于频繁，请稍后再试',
            'ServiceUnavailable': '服务暂时不可用，请稍后重试',
            'Timeout': '请求超时，请检查网络或稍后重试',
        }
        
        friendly_msg = error_map.get(error_code, error_message)
        detail = f"[{error_code}] {friendly_msg}"
        if request_id:
            detail += f" (请求ID: {request_id})"
        
        return detail
    except Exception as e:
        return f"API 返回错误 (HTTP {response.status_code})，但解析响应失败: {str(e)}"


def detect_moyu_mode(commit_logs):
    """
    智能检测是否是摸鱼模式（让用户自己发现这个彩蛋！）
    
    检测逻辑：
    - 提交数量少于 3 个
    - 包含摸鱼关键词
    - 日志总字数少于 100 字
    
    Args:
        commit_logs: 提交日志内容
    
    Returns:
        bool: True表示摸鱼模式
    """
    logs_lower = commit_logs.lower()
    
    # 1. 检查摸鱼关键词
    for keyword in MOYU_KEYWORDS:
        if keyword.lower() in logs_lower:
            return True
    
    # 2. 检查提交数量（按行数估算）
    lines = [line.strip() for line in commit_logs.split('\n') if line.strip()]
    if len(lines) < MOYU_COMMIT_THRESHOLD:
        return True
    
    # 3. 检查总字数（少于100字可能是摸鱼）
    if len(commit_logs) < 100:
        return True
    
    return False


def call_dashscope_api(api_key, model, commit_logs, today, is_moyu_mode=False):
    """
    调用 DashScope API 生成日报
    
    Args:
        api_key: API密钥
        model: 模型名称
        commit_logs: 提交日志
        today: 今日日期
        is_moyu_mode: 是否摸鱼模式
    
    Returns:
        tuple: (success: bool, result: str, error_detail: dict, is_moyu: bool)
    """
    # 选择提示词模板
    if is_moyu_mode:
        system_prompt = MOYU_PROMPT_TEMPLATE.format(today=today)
    else:
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(today=today)
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    payload = {
        'model': model,
        'input': {
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f'请根据以下代码提交日志生成日报：\n\n{commit_logs}'}
            ]
        },
        'parameters': {
            'result_format': 'message',
            'max_tokens': 2000
        }
    }
    
    try:
        response = requests.post(
            DASHSCOPE_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # 验证响应结构
                if 'output' not in data:
                    return False, None, {
                        'type': 'invalid_response',
                        'message': 'API 响应格式异常：缺少 output 字段',
                        'detail': f'完整响应: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}'
                    }
                
                if 'choices' not in data['output'] or len(data['output']['choices']) == 0:
                    return False, None, {
                        'type': 'invalid_response',
                        'message': 'API 响应格式异常：缺少 choices 字段或为空',
                        'detail': f'output 内容: {json.dumps(data["output"], ensure_ascii=False, indent=2)[:500]}'
                    }
                
                choice = data['output']['choices'][0]
                if 'message' not in choice or 'content' not in choice['message']:
                    return False, None, {
                        'type': 'invalid_response',
                        'message': 'API 响应格式异常：缺少 message.content 字段',
                        'detail': f'choice 内容: {json.dumps(choice, ensure_ascii=False, indent=2)[:500]}'
                    }
                
                report_content = choice['message']['content']
                
                if not report_content or not report_content.strip():
                    return False, None, {
                        'type': 'empty_response',
                        'message': 'API 返回了空内容，请检查输入或稍后重试',
                        'detail': '模型没有生成任何内容'
                    }
                
                return True, report_content, None, is_moyu_mode
                
            except json.JSONDecodeError as e:
                return False, None, {
                    'type': 'json_decode_error',
                    'message': '解析 API 响应失败：返回的不是有效 JSON',
                    'detail': f'错误: {str(e)}，原始响应: {response.text[:500]}'
                }, is_moyu_mode
            except (KeyError, IndexError) as e:
                return False, None, {
                    'type': 'response_structure_error',
                    'message': 'API 响应结构不符合预期',
                    'detail': f'错误: {str(e)}，响应: {response.text[:500]}'
                }, is_moyu_mode
        
        # HTTP 错误处理
        error_msg = parse_api_error(response)
        return False, None, {
            'type': 'api_error',
            'message': error_msg,
            'detail': f'HTTP 状态码: {response.status_code}'
        }, is_moyu_mode
        
    except requests.exceptions.Timeout:
        return False, None, {
            'type': 'timeout',
            'message': '请求超时 (60秒)，请检查网络连接或稍后重试',
            'detail': 'API 服务器在 60 秒内未响应'
        }, is_moyu_mode
        
    except requests.exceptions.ConnectionError as e:
        return False, None, {
            'type': 'connection_error',
            'message': '网络连接失败，请检查网络或防火墙设置',
            'detail': f'错误详情: {str(e)}'
        }, is_moyu_mode
        
    except requests.exceptions.RequestException as e:
        return False, None, {
            'type': 'request_error',
            'message': '请求发送失败',
            'detail': f'错误类型: {type(e).__name__}, 详情: {str(e)}'
        }, is_moyu_mode


# 读取配置
config = get_config()


@app.route('/')
def index():
    """首页"""
    return render_template('index.html', default_model=config['model'])


@app.route('/generate', methods=['POST'])
def generate_report():
    """生成日报 API（自动检测摸鱼模式）"""
    data = request.json or {}
    
    # 参数提取和验证
    commit_logs = str(data.get('commit_logs', '')).strip()
    api_key = str(data.get('api_key', '')).strip() or config['api_key']
    model = str(data.get('model', '')).strip() or config['model']
    
    # 验证提交日志
    if not commit_logs:
        return jsonify({
            'success': False,
            'error': {
                'type': 'validation_error',
                'message': '请输入代码提交日志',
                'detail': 'commit_logs 字段不能为空'
            }
        }), 400
    
    if len(commit_logs) > MAX_LOG_LENGTH:
        return jsonify({
            'success': False,
            'error': {
                'type': 'validation_error',
                'message': f'提交日志过长（{len(commit_logs)} 字符），请控制在 {MAX_LOG_LENGTH} 字符以内',
                'detail': f'超出 {len(commit_logs) - MAX_LOG_LENGTH} 字符'
            }
        }), 400
    
    # 验证 API Key
    if not api_key:
        return jsonify({
            'success': False,
            'error': {
                'type': 'config_error',
                'message': '未配置 API Key',
                'detail': '请在 config.ini 中配置 api_key，或在请求中传入 api_key 字段'
            }
        }), 400
    
    # 验证模型名称格式（简单校验）
    if not model:
        return jsonify({
            'success': False,
            'error': {
                'type': 'validation_error',
                'message': '模型名称不能为空',
                'detail': '请在输入框中输入模型名称，或使用默认配置'
            }
        }), 400
    
    # 自动检测摸鱼模式（让用户自己发现这个彩蛋！）
    is_moyu_mode = detect_moyu_mode(commit_logs)
    
    # 获取今日日期
    today = get_today()
    
    # 调用 API
    success, report_content, error, detected_moyu = call_dashscope_api(
        api_key, model, commit_logs, today, is_moyu_mode
    )
    
    if success:
        return jsonify({
            'success': True,
            'report': report_content,
            'meta': {
                'model': model,
                'date': today,
                'is_moyu': detected_moyu
            }
        })
    else:
        return jsonify({
            'success': False,
            'error': error
        }), 500


@app.route('/config', methods=['GET'])
def get_config_status():
    """获取配置状态（不包含敏感信息）"""
    return jsonify({
        'has_api_key': bool(config['api_key']),
        'default_model': config['model']
    })


@app.route('/download', methods=['POST'])
def download_report():
    """下载日报文件"""
    data = request.json or {}
    content = str(data.get('content', ''))
    
    if not content.strip():
        return jsonify({
            'success': False,
            'error': {
                'type': 'validation_error',
                'message': '内容为空，无法下载',
                'detail': 'content 字段不能为空或仅包含空白字符'
            }
        }), 400
    
    # 生成文件名
    try:
        today = datetime.now(timezone.utc).astimezone().strftime('%Y%m%d')
    except Exception:
        today = datetime.now().strftime('%Y%m%d')
    
    filename = f'日报_{today}.md'
    
    # 创建内存文件
    try:
        file_io = io.BytesIO(content.encode('utf-8'))
        file_io.seek(0)
        
        return send_file(
            file_io,
            mimetype='text/markdown',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'type': 'file_error',
                'message': '生成文件失败',
                'detail': str(e)
            }
        }), 500


@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({
        'success': False,
        'error': {
            'type': 'not_found',
            'message': '请求的资源不存在',
            'detail': f'路径: {request.path}'
        }
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    return jsonify({
        'success': False,
        'error': {
            'type': 'internal_error',
            'message': '服务器内部错误',
            'detail': str(error)
        }
    }), 500


if __name__ == '__main__':
    app.run(
        debug=config['debug'],
        host=config['host'],
        port=config['port']
    )
