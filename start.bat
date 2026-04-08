@echo off
chcp 65001 >nul
echo ==========================================
echo       日报生成器 - 启动脚本
echo ==========================================
echo.

:: 切换到脚本所在目录
cd /d "%~dp0"

:: 检查虚拟环境是否存在
if not exist "venv\Scripts\python.exe" (
    echo [1/3] 正在创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败，请确保已安装Python 3.8+
        pause
        exit /b 1
    )
)

:: 激活虚拟环境
call venv\Scripts\activate.bat

:: 检查是否需要安装依赖
echo [2/3] 正在检查依赖...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements.txt
) else (
    echo 依赖已满足
)

echo.
echo [3/3] 正在启动服务...
echo.

echo ==========================================
echo  服务地址: http://localhost:5000
echo  按 Ctrl+C 停止服务
echo ==========================================
echo.

python app.py

echo.
echo 服务已停止
pause
