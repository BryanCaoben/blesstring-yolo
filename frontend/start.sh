#!/bin/bash
# 前端服务启动脚本

echo "启动乐器瑕疵检测前端服务..."

# 检查node_modules是否存在
if [ ! -d "node_modules" ]; then
    echo "正在安装依赖..."
    npm install
fi

# 启动开发服务器
echo "启动前端开发服务器在 http://localhost:3000"
npm run dev

