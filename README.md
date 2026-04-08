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

#### 方式二：环境变量

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

#### 方式三：Flask 配置

```bash
# 可选配置
export FLASK_DEBUG=false      # 调试模式
export FLASK_PORT=5000        # 服务端口
export FLASK_HOST=0.0.0.0     # 监听地址
```

## 📋 使用流程

1. **准备代码日志**：复制你的 Git/SVN 提交日志
2. **粘贴日志**：在网页左侧输入框粘贴提交日志
3. **选择模型**（可选）：tongyi-xiaomi-analysis-pro / qwen-turbo / qwen-plus / qwen-max
4. **生成日报**：点击生成按钮，AI 自动提炼工作成果
5. **导出结果**：支持下载 `.md` 文件或复制到剪贴板

## 📝 示例

### 输入：流水账式的 Git 提交日志

```
a1b2c3d fix: 修复了登录页面密码框不能输入特殊字符的问题
e4f5g6h feat: 用户管理模块新增批量导入功能
i7j8k9l refactor: 优化了订单查询 SQL，加了索引
m0n1o2p fix: 解决了 iOS 上日期选择器显示错位
q3r4s5t docs: 更新了 API 接口文档
t6u7v8w style: 统一了按钮样式
x9y0z1a test: 写了用户模块的单元测试
b2c3d4e merge: 合并 feature/user-auth 分支
f5g6h7i fix: 又改了个 Bug，用户反馈点击没反应
j8k9l0m chore: 升级了依赖包版本
n1o2p3q feat: 完成了报表导出功能
r4s5t6u fix: 报表导出中文乱码问题解决
v7w8x9y refactor: 代码 review 后优化了部分逻辑
z0a1b2c fix: 紧急修复线上支付回调问题
```

### 输出：结构化工作日报

```markdown
## 工作日报 - 2024年04月08日

### 一、功能开发
- 完成了用户管理模块的批量导入功能开发
- 实现了报表导出功能，支持 Excel 格式下载

### 二、Bug 修复
- 修复了登录页面密码输入框无法使用特殊字符的问题
- 解决了 iOS 设备上日期选择器组件显示错位的问题
- 处理了用户反馈的点击无响应问题
- 紧急修复了线上支付回调接口异常问题
- 解决了报表导出时中文乱码的问题

### 三、代码优化
- 对订单查询 SQL 进行了性能优化，新增索引提升查询效率
- 根据代码 Review 反馈优化了核心业务逻辑

### 四、其他工作
- 更新了 API 接口文档，补充了最新接口说明
- 统一了前端按钮组件样式规范
- 完成了用户模块的单元测试覆盖
- 合并了用户认证特性分支到主分支
- 升级了项目依赖包至最新稳定版本

### 四、今日总结
今日主要围绕用户管理模块功能完善展开，完成了批量导入和报表导出两个核心功能，同时修复了 5 个线上及测试环境 Bug，并对系统性能进行了优化。整体开发进度符合预期。

### 五、明日计划
1. 继续完善报表模块的筛选功能
2. 跟进支付回调监控报警配置
3. 进行新版本的功能回归测试
```

---

## 🐟 摸鱼日报模式

专为"今天啥也没干"的日子准备的特殊模式！

### 自动检测
系统会根据提交日志自动判断你是否在摸鱼：
- 提交数量少于 3 个
- 包含摸鱼关键词（如"摸鱼"、"fix typo"、"wip"等）
- 日志总字数少于 100 字

也可以手动切换到 🐟 摸鱼日报模式

### 摸鱼日报示例

**输入（只有1个提交）：**
```
a1b2c3d fix: 修改了一个错别字
```

**输出（一本正经胡说八道）：**
```markdown
## 摸鱼日报 - 2024年04月08日

### 一、文本精准化工程
- 对系统文本进行了深度精细化治理，显著提升了用户体验的丝滑度

### 二、战略性代码审查
- 进行了长达3小时的全量代码走读，识别出3处潜在优化点（其实就看了看）

### 三、跨部门协同沟通
- 积极参与了茶水间的非正式技术交流，有效促进了团队凝聚力建设

### 四、深度技术钻研
- 对明日技术方案进行了前瞻性思考，形成了初步脑图（在脑子里）

### 五、生理机能维护
- 进行了多轮眼部保健操和颈椎放松运动，确保可持续战斗力

### 四、今日总结
今日工作量饱满，在多维度取得了突破性进展。虽然代码产出较少，但在技术沉淀、团队协同、身心健康等方面均有显著建树，为后续高强度开发奠定了坚实基础。

### 五、明日计划
1. 继续深化技术方案设计
2. 推进跨部门协同事项落地
3. 优化个人工作流效率
```

**特点：**
- 把"改错别字"说成"文本精准化工程"
- 把"喝水聊天"说成"跨部门协同沟通"
- 把"发呆"说成"深度技术钻研"
- 互联网黑话拉满：赋能、抓手、闭环、底层逻辑...

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
