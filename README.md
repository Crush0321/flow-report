# 📝 日报生成器

基于通义千问大模型，智能从代码提交日志生成工作日报。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ 功能特点

- 🤖 **AI 智能生成** - 基于通义千问大模型，自动提炼工作成果
- 🎨 **现代化 UI** - 简洁美观的网页界面，支持响应式布局
- ⚙️ **灵活配置** - 支持配置文件和环境变量
- 📥 **一键导出** - 支持下载 Markdown 文件或复制内容
- 🔒 **安全隔离** - 使用虚拟环境，配置文件不提交到 Git
- ⌨️ **快捷操作** - 支持 `Ctrl+Enter` 快速生成

## 🚀 快速开始

### 方式一：一键启动（Windows）

```bash
# 克隆仓库
git clone https://github.com/Crush0321/flow-report.git
cd flow-report

# 运行启动脚本
start.bat
```

### 方式二：手动启动

```bash
# 1. 克隆仓库
git clone https://github.com/Crush0321/flow-report.git
cd flow-report

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 创建配置文件
cp config.ini.example config.ini

# 6. 编辑配置文件，填入你的 API Key
# 使用记事本或其他编辑器打开 config.ini

# 7. 启动服务
python app.py
```

访问 http://localhost:5000 即可使用。

## ⚙️ 配置说明

### 配置文件

复制 `config.ini.example` 为 `config.ini`：

```ini
# 通义千问 API 配置
[dashscope]
api_key = your_api_key_here
model = qwen-turbo

# Flask 配置
[flask]
debug = false
port = 5000
host = 0.0.0.0
```

### 获取 API Key

1. 前往 [阿里云 DashScope](https://dashscope.aliyun.com/)
2. 注册/登录阿里云账号
3. 创建 API Key
4. 将 API Key 填入 `config.ini`

### 环境变量（可选）

你也可以通过环境变量配置，优先级高于配置文件：

```bash
export DASHSCOPE_API_KEY=your_api_key_here
export DASHSCOPE_MODEL=qwen-turbo
export FLASK_DEBUG=false
export FLASK_PORT=5000
```

## 📋 使用流程

1. **准备代码日志**：复制你的 Git/SVN 提交日志
2. **粘贴日志**：在网页左侧输入框粘贴提交日志
3. **选择模型**（可选）：qwen-turbo(快) / qwen-plus(均衡) / qwen-max(强)
4. **生成日报**：点击生成按钮，AI 自动提炼工作成果
5. **导出结果**：支持下载 `.md` 文件或复制到剪贴板

## 🛠️ 技术栈

- **后端**: Flask + Python 3.8+
- **前端**: HTML5 + CSS3 + Vanilla JS
- **AI**: 阿里云 DashScope API (通义千问)

## 📝 项目结构

```
flow-report/
├── app.py              # Flask 后端服务
├── config.py           # 配置文件管理
├── config.ini          # 配置文件（本地创建，不提交）
├── config.ini.example  # 配置文件模板
├── requirements.txt    # Python 依赖
├── start.bat          # Windows 启动脚本
├── start.sh           # macOS/Linux 启动脚本
├── .gitignore         # Git 忽略文件
├── README.md          # 项目说明
└── templates/
    └── index.html     # 前端页面
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 开源协议

本项目基于 [MIT](LICENSE) 协议开源。
