@echo off
REM Windows后端服务启动脚本

echo 启动乐器瑕疵检测后端服务...

REM 激活虚拟环境（如果存在）
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo 已激活虚拟环境
)

REM 检查依赖
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements.txt
)

REM 创建必要的目录
if not exist ..\uploads mkdir ..\uploads
if not exist ..\models mkdir ..\models

REM 启动服务
echo 启动FastAPI服务在 http://0.0.0.0:8000
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

