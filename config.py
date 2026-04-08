"""
配置文件管理模块
"""
import os
import configparser
from pathlib import Path

# 配置文件路径
CONFIG_FILE = Path(__file__).parent / 'config.ini'


def get_config():
    """
    读取配置文件，如果不存在则返回默认配置
    """
    config = configparser.ConfigParser()
    
    if CONFIG_FILE.exists():
        config.read(CONFIG_FILE, encoding='utf-8')
    
    # 确保有必要的配置节
    if 'dashscope' not in config:
        config['dashscope'] = {}
    if 'flask' not in config:
        config['flask'] = {}
    
    # 从环境变量读取配置（优先级最高）
    dashscope_config = config['dashscope']
    flask_config = config['flask']
    
    return {
        'api_key': os.getenv('DASHSCOPE_API_KEY') or dashscope_config.get('api_key', ''),
        'model': os.getenv('DASHSCOPE_MODEL') or dashscope_config.get('model', 'qwen-turbo'),
        'debug': os.getenv('FLASK_DEBUG', 'false').lower() == 'true' or flask_config.getboolean('debug', False),
        'port': int(os.getenv('FLASK_PORT') or flask_config.get('port', 5000)),
        'host': os.getenv('FLASK_HOST') or flask_config.get('host', '0.0.0.0'),
    }


def create_config_template():
    """
    创建配置文件模板
    """
    if not CONFIG_FILE.exists():
        example_file = Path(__file__).parent / 'config.ini.example'
        if example_file.exists():
            import shutil
            shutil.copy(example_file, CONFIG_FILE)
            print(f"✅ 已创建配置文件模板: {CONFIG_FILE}")
            print("📝 请编辑 config.ini 文件，填入你的 API Key")
            return True
    return False


if __name__ == '__main__':
    create_config_template()
    print("\n当前配置:")
    config = get_config()
    for key, value in config.items():
        if 'key' in key.lower() and value:
            value = value[:10] + '...'  # 隐藏敏感信息
        print(f"  {key}: {value}")
