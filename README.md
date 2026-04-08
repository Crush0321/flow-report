# 📝 日报生成器

基于通义千问大模型，智能生成开发工作日报。支持文字描述、代码分析、混合模式三种输入方式。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ 功能特点

- 🤖 **AI 智能生成** - 基于通义千问大模型，自动提炼工作成果
- 📝 **三种输入模式** - 文字描述、代码分析、混合模式自由切换
- 📄 **代码智能分析** - 自动识别代码语言，提取关键信息生成日报
- 🎨 **现代化 UI** - 简洁美观的网页界面，支持响应式布局
- ⚙️ **灵活配置** - 支持配置文件和环境变量
- 📥 **一键导出** - 支持下载 Markdown 文件或复制内容
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

# 5. 启动服务
python app.py
```

访问 http://localhost:5000 即可使用。

## ⚙️ 配置说明

### 获取 API Key

1. 前往 [阿里云 DashScope](https://dashscope.aliyun.com/)
2. 注册/登录阿里云账号
3. 创建 API Key

### 配置方式

#### 方式一：网页输入（推荐）

启动后直接在网页表单中输入：
- **API Key**：从 DashScope 获取的 Key
- **模型名称**：如 `tongyi-xiaomi-analysis-pro`、`qwen-turbo` 等

#### 方式二：配置文件

创建 `config.ini` 文件：

```ini
[dashscope]
api_key = sk-your-api-key-here
model = tongyi-xiaomi-analysis-pro

[flask]
debug = false
port = 5000
host = 0.0.0.0
```

#### 方式三：环境变量

通过环境变量配置（优先级最高）：

```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY="your_api_key_here"
$env:DASHSCOPE_MODEL="tongyi-xiaomi-analysis-pro"

# Windows CMD
set DASHSCOPE_API_KEY=your_api_key_here
set DASHSCOPE_MODEL=tongyi-xiaomi-analysis-pro

# macOS/Linux
export DASHSCOPE_API_KEY=your_api_key_here
export DASHSCOPE_MODEL=tongyi-xiaomi-analysis-pro
```

**优先级**：环境变量 > config.ini > 默认值

## 📋 使用指南

### 三种输入模式

#### 1️⃣ 文字描述模式

适用于：有工作记录、Git日志、或想直接描述工作内容

**示例输入：**
```
今天完成了用户登录模块的开发：
1. 实现了JWT token认证机制
2. 集成了短信验证码登录
3. 修复了验证码过期时间不生效的bug
```

**示例输出：**
```markdown
## 工作日报 - 2024年04月08日

### 一、功能开发
- 完成了用户登录模块的开发，实现了JWT token认证机制
- 集成了短信验证码登录功能，提升了用户体验

### 二、Bug修复
- 修复了验证码过期时间不生效的问题，确保系统安全性

### 三、今日总结
今日主要完成用户认证模块的核心功能开发...

### 四、明日计划
1. 继续完善用户注册功能
2. 进行登录模块的接口测试
```

#### 2️⃣ 代码文件模式

适用于：写了代码但不想写描述，让AI分析代码生成日报

**操作步骤：**
1. 切换到"代码文件"标签
2. 拖拽或点击上传代码文件（支持多文件）
3. （可选）添加代码描述帮助AI理解
4. 点击生成

**支持的文件类型：**
- Python (.py)
- JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
- Java (.java)
- Go (.go)
- Rust (.rs)
- C/C++ (.c, .cpp, .h)
- C# (.cs)
- PHP (.php)
- Ruby (.rb)
- Swift (.swift)
- Kotlin (.kt)
- 以及更多...

**示例输出：**
```markdown
## 工作日报 - 2024年04月08日

### 一、主要开发内容
- 完成了用户认证模块的开发，实现了基于JWT的登录鉴权

### 二、技术亮点
- 使用 bcrypt 进行密码加密存储
- 采用 Redis 缓存登录状态
- 实现了 token 自动刷新机制

### 三、代码统计
- 涉及文件: 3 个
- 代码规模: 约 450 行
- 主要语言: Python

### 四、今日总结...
```

#### 3️⃣ 混合模式

适用于：既有文字描述又有代码，想要更全面的日报

**特点：**
- 文字描述作为主线
- 代码分析作为补充验证
- 生成更全面的工作内容总结

### 导出日报

生成日报后，可以：
- **下载 Markdown**：保存为 `.md` 文件
- **复制内容**：一键复制到剪贴板，方便粘贴到邮件、IM工具等

## 📝 示例

### 示例 1：文字描述

**输入：**
```
a1b2c3d feat: 完成用户登录功能
e4f5g6h fix: 修复订单列表分页bug
i7j8k9l refactor: 优化数据库查询性能
```

**输出：** 结构化的工作日报，按功能开发、Bug修复、代码优化分类

### 示例 2：代码分析

**上传文件：** `user_service.py`, `auth_middleware.py`

**输出：**
```markdown
## 工作日报 - 2024年04月08日

### 一、主要开发内容
- 完成了用户服务层的重构，优化了认证流程

### 二、技术亮点
- 使用装饰器模式实现权限校验中间件
- 引入连接池提升数据库访问性能

### 三、代码统计
- 涉及文件: 2 个
- 代码规模: 约 300 行
- 主要语言: Python

### 四、今日总结
今日主要完成用户认证模块的重构工作...
```

## 🛠️ 技术栈

- **后端**: Flask + Python 3.8+
- **前端**: HTML5 + CSS3 + Vanilla JS
- **AI**: 阿里云 DashScope API (通义千问)

## 📝 项目结构

```
flow-report/
├── app.py              # Flask 后端服务（包含配置读取）
├── config.ini          # 配置文件（本地创建，不提交）
├── requirements.txt    # Python 依赖
├── start.bat          # Windows 一键启动脚本
├── start.sh           # macOS/Linux 启动脚本
├── .gitignore         # Git 忽略文件
├── README.md          # 项目说明
└── templates/
    └── index.html     # 前端页面
```

## 🔒 安全说明

- 配置文件 `config.ini` 已加入 `.gitignore`，不会被提交到Git
- 建议通过环境变量配置 API Key，更加安全
- 上传的代码文件仅用于生成日报，不会被保存或传输到第三方

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 开源协议

本项目基于 [MIT](LICENSE) 协议开源。
