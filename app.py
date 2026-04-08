"""
日报生成器 - Flask 后端服务
支持：文本描述生成日报、代码分析生成日报、混合模式
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

app = Flask(__name__)

# 常量配置
CONFIG_FILE = Path(__file__).parent / 'config.ini'
DASHSCOPE_API_URL = os.getenv('DASHSCOPE_API_URL', 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation')
MAX_LOG_LENGTH = 10000
MAX_CODE_SIZE = 1024 * 1024  # 1MB
MAX_CODE_FILES = 5
DEFAULT_MODEL = 'tongyi-xiaomi-analysis-pro'
DEFAULT_PORT = 5000
DEFAULT_HOST = '0.0.0.0'

# 支持的代码文件扩展名
CODE_EXTENSIONS = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.jsx': 'React JSX',
    '.tsx': 'React TSX',
    '.java': 'Java',
    '.go': 'Go',
    '.rs': 'Rust',
    '.c': 'C',
    '.cpp': 'C++',
    '.h': 'C/C++ Header',
    '.hpp': 'C++ Header',
    '.cs': 'C#',
    '.php': 'PHP',
    '.rb': 'Ruby',
    '.swift': 'Swift',
    '.kt': 'Kotlin',
    '.scala': 'Scala',
    '.r': 'R',
    '.m': 'Objective-C/MATLAB',
    '.mm': 'Objective-C++',
    '.sql': 'SQL',
    '.sh': 'Shell',
    '.bash': 'Bash',
    '.ps1': 'PowerShell',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.json': 'JSON',
    '.xml': 'XML',
    '.toml': 'TOML',
    '.ini': 'INI',
    '.cfg': 'Config',
    '.md': 'Markdown',
    '.html': 'HTML',
    '.htm': 'HTML',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.sass': 'Sass',
    '.less': 'Less',
    '.vue': 'Vue',
    '.svelte': 'Svelte',
}

# 提示词模板 - 基于文本描述生成日报（支持任意工作描述）
TEXT_REPORT_PROMPT = """你是一位资深的软件开发工程师和技术写作专家，擅长将工作内容提炼成专业的日报。

请根据用户提供的**工作描述**，生成一份结构清晰、专业的工作日报。

工作描述可以是：
- 今天完成的工作内容描述
- Git/SVN 提交日志
- 项目进展说明
- 任意形式的工作记录

要求：
1. 按工作类别分类（如：功能开发、Bug修复、代码优化、文档更新、会议沟通等）
2. 每项工作用一句话概括，突出价值和成果，不要罗列细节
3. 包含今日工作总结和明日工作建议
4. 使用Markdown格式输出
5. 语言简洁专业，适合向上级汇报
6. 如果描述不够详细，适当合理推测补充，但不要过度发挥

重要：今天是 {today}，日报标题必须准确使用这个日期。

输出格式：
## 工作日报 - {today}

### 一、功能开发（或其他类别）
- 完成了xxx，实现了xxx效果

### 二、Bug修复（如有）
- 修复了xxx问题，提升了xxx

### 三、其他工作（如有）
- xxx

### 四、今日总结
今日主要完成了...

### 五、明日计划
1. xxx
2. xxx
"""

# 提示词模板 - 基于代码分析生成日报
CODE_REPORT_PROMPT = """你是一位资深的代码审查专家和技术负责人，擅长从代码变更中洞察工作价值。

请根据用户提供的**代码文件内容**，分析并生成一份专业的开发工作日报。

分析维度：
1. **功能理解**：这段代码实现了什么功能/模块
2. **技术亮点**：使用了什么技术/框架/设计模式
3. **工作量评估**：代码规模、复杂度、涉及文件数
4. **业务价值**：这个功能解决了什么问题，带来什么价值

要求：
1. 用业务语言描述技术实现，不要罗列代码细节
2. 突出技术难点和解决方案
3. 估算工作量和复杂度
4. 使用Markdown格式，语言专业简洁
5. 如果提供了代码描述，结合描述一起分析；如果没有，仅根据代码内容分析

重要：今天是 {today}，日报标题必须准确使用这个日期。

输出格式：
## 工作日报 - {today}

### 一、主要开发内容
- 完成了 xxx 模块/功能的开发
- 实现了 xxx 业务逻辑

### 二、技术亮点
- 使用 xxx 技术/框架
- 解决了 xxx 技术难点
- 采用了 xxx 设计思路

### 三、代码统计
- 涉及文件: n 个
- 代码规模: xxx 行（估算）
- 主要语言: xxx

### 四、今日总结
...

### 五、明日计划
1. ...
2. ...
"""

# 提示词模板 - 文本+代码混合模式
MIXED_REPORT_PROMPT = """你是一位资深的全栈技术专家，擅长整合多种信息源生成全面的工作日报。

请根据用户提供的**工作描述**和**代码文件内容**，综合分析并生成一份完整的工作日报。

整合策略：
1. **工作描述**：理解用户的主观工作记录和计划
2. **代码分析**：验证和补充代码层面的客观产出
3. **交叉印证**：将描述和代码结合，生成更准确的日报

要求：
1. 以工作描述为主线，代码分析为补充
2. 突出工作成果和业务价值
3. 不要罗列代码细节，用业务语言描述
4. 使用Markdown格式，语言专业简洁

重要：今天是 {today}，日报标题必须准确使用这个日期。

输出格式：
## 工作日报 - {today}

### 一、主要工作成果
- 完成了 xxx
- 实现了 xxx

### 二、技术实现（基于代码分析）
- 使用 xxx 技术
- 解决了 xxx 问题

### 三、代码概况
- 文件数: n 个
- 主要语言: xxx

### 四、今日总结
...

### 五、明日计划
1. ...
2. ...
"""

# 摸鱼模式已暂时关闭
# MOYU_PROMPT_TEMPLATE = """..."""


def get_today():
    """获取带时区的今日日期（中文格式）"""
    try:
        return datetime.now(timezone.utc).astimezone().strftime('%Y年%m月%d日')
    except Exception:
        return datetime.now().strftime('%Y年%m月%d日')


def get_date_str(format='%Y%m%d'):
    """获取日期字符串（用于文件名）"""
    try:
        return datetime.now(timezone.utc).astimezone().strftime(format)
    except Exception:
        return datetime.now().strftime(format)


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


def parse_code_file(file_content, filename):
    """解析单个代码文件，提取信息"""
    lines = file_content.split('\n')
    line_count = len(lines)
    
    # 获取语言
    ext = Path(filename).suffix.lower()
    language = CODE_EXTENSIONS.get(ext, 'Unknown')
    
    # 提取导入语句（简单统计）
    imports = []
    if ext == '.py':
        import_pattern = re.compile(r'^(import|from)\s+([\w.]+)')
        for line in lines[:50]:  # 只看前50行
            match = import_pattern.match(line.strip())
            if match:
                imports.append(match.group(2).split('.')[0])
    elif ext in ['.js', '.ts', '.jsx', '.tsx']:
        import_pattern = re.compile(r"^import.*from\s+['\"]([@\w-/]+)['\"]")
        for line in lines[:50]:
            match = import_pattern.match(line.strip())
            if match:
                imports.append(match.group(1).split('/')[0])
    
    # 提取函数/类定义（简单统计）
    definitions = []
    if ext == '.py':
        def_pattern = re.compile(r'^(def|class)\s+(\w+)')
        for line in lines:
            match = def_pattern.match(line.strip())
            if match:
                definitions.append(match.group(2))
    elif ext in ['.js', '.ts', '.jsx', '.tsx']:
        def_pattern = re.compile(r'^(function|const|let|var|class)\s+(\w+)')
        for line in lines:
            match = def_pattern.match(line.strip())
            if match:
                definitions.append(match.group(2))
    elif ext == '.java':
        def_pattern = re.compile(r'^(public|private|protected)?\s*(static)?\s*(\w+)\s+(\w+)\s*\(')
        for line in lines:
            match = def_pattern.match(line.strip())
            if match:
                definitions.append(match.group(4))
    
    return {
        'filename': filename,
        'language': language,
        'line_count': line_count,
        'imports': list(set(imports))[:10],  # 去重，最多10个
        'definitions': definitions[:10],  # 最多10个
        'preview': '\n'.join(lines[:30])  # 前30行预览
    }


def format_code_for_prompt(files_info):
    """将代码文件信息格式化为提示词"""
    total_lines = sum(f['line_count'] for f in files_info)
    languages = {}
    for f in files_info:
        lang = f['language']
        languages[lang] = languages.get(lang, 0) + 1
    
    main_language = max(languages, key=languages.get) if languages else 'Unknown'
    
    result = f"【代码概览】\n"
    result += f"- 文件数: {len(files_info)} 个\n"
    result += f"- 总行数: {total_lines} 行\n"
    result += f"- 主要语言: {main_language}\n\n"
    
    result += "【文件详情】\n"
    for i, info in enumerate(files_info, 1):
        result += f"\n--- 文件 {i}: {info['filename']} ({info['language']}, {info['line_count']} 行) ---\n"
        if info['imports']:
            result += f"主要依赖: {', '.join(info['imports'])}\n"
        if info['definitions']:
            result += f"主要定义: {', '.join(info['definitions'][:5])}\n"
        result += "\n代码预览:\n"
        result += "```\n" + info['preview'] + "\n```\n"
    
    return result


def parse_api_error(response):
    """解析 API 错误响应"""
    try:
        data = response.json()
        error_code = data.get('code', 'Unknown')
        error_message = data.get('message', '未知错误')
        request_id = data.get('request_id', '')
        
        error_map = {
            'InvalidApiKey': 'API Key 无效或已过期',
            'InsufficientBalance': '账户余额不足',
            'AccessDenied': '无权限访问该模型',
            'ModelNotFound': '模型不存在',
            'ContextLengthExceeded': '输入内容过长',
            'RateLimitExceeded': '请求过于频繁',
            'ServiceUnavailable': '服务暂时不可用',
            'Timeout': '请求超时',
        }
        
        friendly_msg = error_map.get(error_code, error_message)
        detail = f"[{error_code}] {friendly_msg}"
        if request_id:
            detail += f" (请求ID: {request_id})"
        return detail
    except Exception as e:
        return f"API 错误 (HTTP {response.status_code}): {str(e)}"


def call_dashscope_api(api_key, model, prompt_type, today, text_content='', code_content=''):
    """
    调用 DashScope API 生成日报
    
    Args:
        api_key: API密钥
        model: 模型名称
        prompt_type: 'text' | 'code' | 'mixed'
        today: 今日日期
        text_content: 文本描述内容
        code_content: 代码内容
    
    Returns:
        tuple: (success, result, error)
    """
    # 选择提示词模板
    if prompt_type == 'code' and code_content:
        system_prompt = CODE_REPORT_PROMPT.format(today=today)
        user_content = f"请分析以下代码并生成日报:\n\n{code_content}"
    elif prompt_type == 'mixed' and text_content and code_content:
        system_prompt = MIXED_REPORT_PROMPT.format(today=today)
        user_content = f"【工作描述】\n{text_content}\n\n{code_content}\n\n请根据以上信息生成日报。"
    else:
        system_prompt = TEXT_REPORT_PROMPT.format(today=today)
        user_content = f"请根据以下工作描述生成日报:\n\n{text_content}"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    payload = {
        'model': model,
        'input': {
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_content}
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
            timeout=90
        )
        
        if response.status_code == 200:
            data = response.json()
            try:
                content = data['output']['choices'][0]['message']['content']
                if content and content.strip():
                    return True, content.strip(), None
                return False, None, {'type': 'empty', 'message': '模型返回空内容'}
            except (KeyError, IndexError) as e:
                return False, None, {
                    'type': 'parse_error',
                    'message': '解析响应失败',
                    'detail': str(e)
                }
        
        return False, None, {
            'type': 'api_error',
            'message': parse_api_error(response)
        }
        
    except requests.exceptions.Timeout:
        return False, None, {'type': 'timeout', 'message': '请求超时 (90秒)'}
    except requests.exceptions.ConnectionError as e:
        return False, None, {'type': 'connection', 'message': '网络连接失败', 'detail': str(e)}
    except Exception as e:
        return False, None, {'type': 'unknown', 'message': '请求失败', 'detail': str(e)}


# 读取配置
config = get_config()


@app.route('/')
def index():
    """首页"""
    return render_template('index.html', default_model=config['model'])


@app.route('/config', methods=['GET'])
def get_config_status():
    """获取配置状态"""
    return jsonify({
        'has_api_key': bool(config['api_key']),
        'default_model': config['model']
    })


@app.route('/generate', methods=['POST'])
def generate_report():
    """
    生成日报 API
    
    支持三种模式：
    1. 仅文本: text 字段有值，code_files 为空
    2. 仅代码: text 可为空或描述，code_files 有值
    3. 混合: text 和 code_files 都有值
    """
    data = request.json or {}
    
    # 参数提取
    text_content = str(data.get('text', '')).strip()
    code_files = data.get('code_files', [])  # 列表，每个元素包含 filename 和 content
    api_key = str(data.get('api_key', '')).strip() or config['api_key']
    model = str(data.get('model', '')).strip() or config['model']
    
    # 验证至少有一种输入
    if not text_content and not code_files:
        return jsonify({
            'success': False,
            'error': {
                'type': 'validation_error',
                'message': '请输入工作描述或上传代码文件',
                'detail': 'text 和 code_files 不能同时为空'
            }
        }), 400
    
    # 验证文本长度
    if text_content and len(text_content) > MAX_LOG_LENGTH:
        return jsonify({
            'success': False,
            'error': {
                'type': 'validation_error',
                'message': f'工作描述过长（{len(text_content)} 字符）',
                'detail': f'请控制在 {MAX_LOG_LENGTH} 字符以内'
            }
        }), 400
    
    # 验证代码文件
    if code_files:
        if len(code_files) > MAX_CODE_FILES:
            return jsonify({
                'success': False,
                'error': {
                    'type': 'validation_error',
                    'message': f'代码文件过多（{len(code_files)} 个）',
                    'detail': f'最多支持 {MAX_CODE_FILES} 个文件'
                }
            }), 400
        
        total_size = sum(len(f.get('content', '')) for f in code_files)
        if total_size > MAX_CODE_SIZE:
            return jsonify({
                'success': False,
                'error': {
                    'type': 'validation_error',
                    'message': f'代码总量过大（{total_size // 1024} KB）',
                    'detail': f'请控制在 {MAX_CODE_SIZE // 1024} KB 以内'
                }
            }), 400
    
    # 验证 API Key
    if not api_key:
        return jsonify({
            'success': False,
            'error': {
                'type': 'config_error',
                'message': '未配置 API Key',
                'detail': '请在环境变量 DASHSCOPE_API_KEY 中配置，或在请求中传入'
            }
        }), 400
    
    # 验证模型
    if not model:
        return jsonify({
            'success': False,
            'error': {
                'type': 'validation_error',
                'message': '模型名称不能为空',
                'detail': '请输入模型名称'
            }
        }), 400
    
    # 处理代码文件
    code_content = ''
    files_info = []
    if code_files:
        for file_data in code_files:
            filename = file_data.get('filename', 'unknown')
            content = file_data.get('content', '')
            if content:
                info = parse_code_file(content, filename)
                files_info.append(info)
        
        if files_info:
            code_content = format_code_for_prompt(files_info)
    
    # 确定模式
    if text_content and code_content:
        prompt_type = 'mixed'
    elif code_content:
        prompt_type = 'code'
    else:
        prompt_type = 'text'
    
    # 获取日期并调用 API
    today = get_today()
    success, report, error = call_dashscope_api(
        api_key, model, prompt_type, today, text_content, code_content
    )
    
    if success:
        return jsonify({
            'success': True,
            'report': report,
            'meta': {
                'model': model,
                'date': today,
                'mode': prompt_type,
                'files_count': len(files_info) if files_info else 0
            }
        })
    else:
        return jsonify({
            'success': False,
            'error': error
        }), 500


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
                'message': '内容为空，无法下载'
            }
        }), 400
    
    filename = f'日报_{get_date_str()}.md'
    
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
    return jsonify({
        'success': False,
        'error': {'type': 'not_found', 'message': '资源不存在'}
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': {'type': 'internal_error', 'message': '服务器内部错误'}
    }), 500


if __name__ == '__main__':
    app.run(
        debug=config['debug'],
        host=config['host'],
        port=config['port']
    )
