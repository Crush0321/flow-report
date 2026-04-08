#!/bin/bash

echo "=========================================="
echo "       日报生成器 - 启动脚本"
echo "=========================================="
echo ""

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 检查虚拟环境是否存在
if [ ! -f "venv/bin/python" ]; then
    echo "[1/3] 正在创建虚拟环境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[错误] 创建虚拟环境失败，请确保已安装Python 3.8+"
        exit 1
    fi
fi

# 激活虚拟环境
source venv/bin/activate

# 检查是否需要安装依赖
echo "[2/3] 正在检查依赖..."
python -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "正在安装依赖..."
    pip install -r requirements.txt
else
    echo "依赖已满足"
fi

echo ""
echo "[3/3] 正在启动服务..."
echo ""

echo "=========================================="
echo "  服务地址: http://localhost:5000"
echo "  按 Ctrl+C 停止服务"
echo "=========================================="
echo ""

python app.py

echo ""
echo "服务已停止"
