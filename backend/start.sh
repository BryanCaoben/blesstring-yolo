#!/bin/bash
# 后端服务启动脚本

echo "启动乐器瑕疵检测后端服务..."

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "已激活虚拟环境"
fi

# 检查依赖
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "正在安装依赖..."
    pip install -r requirements.txt
fi

# 创建必要的目录
mkdir -p ../uploads
mkdir -p ../models

# 启动服务
echo "启动FastAPI服务在 http://0.0.0.0:8000"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

