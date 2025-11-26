# 🚀 部署指南

本指南帮助你在**Ubuntu 24服务器**上部署乐器瑕疵检测系统。

> 💡 **重要提示**：所有服务都在服务器上运行。开发机（Windows）只用于编写代码，不需要安装这些环境。

## 📋 前置要求

### ✅ 已安装（你的服务器上已有）
- ✅ **LabelStudio 1.21.0** - 数据标注工具
- ✅ **ultralytics 8.3.231** - YoloV8模型库

### 📦 需要安装或检查
- Ubuntu 24服务器
- Python 3.9+ 
- Node.js 18+（用于构建前端）
- pip 和 python3-venv

## 🔧 步骤1: 准备服务器环境

### 1.1 更新系统
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 安装Python和必要的工具
```bash
sudo apt install python3 python3-pip python3-venv -y
```

### 1.3 安装Node.js（如果未安装）
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

## 📦 步骤2: 部署后端服务

### 2.1 上传项目文件到服务器
使用scp、rsync或其他方式将项目上传到服务器：
```bash
# 示例：从本地上传
scp -r BlesstringYolo/ user@your-server-ip:/path/to/project/
```

### 2.2 进入后端目录
```bash
cd /path/to/project/BlesstringYolo/backend
```

### 2.3 创建Python虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2.4 安装Python依赖
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.5 配置环境变量（可选）
```bash
# 创建.env文件
nano .env
```

添加以下内容：
```env
LABEL_STUDIO_URL=http://localhost:8080
LABEL_STUDIO_API_KEY=your_labelstudio_api_key
YOLO_MODEL_PATH=yolov8n.pt
```

### 2.6 创建必要的目录
```bash
mkdir -p ../uploads
mkdir -p ../models
```

### 2.7 测试启动后端服务
```bash
# 使用启动脚本
chmod +x start.sh
./start.sh

# 或者直接使用uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

访问 http://your-server-ip:8000/docs 验证API文档是否正常显示。

### 2.8 使用systemd创建后端服务（生产环境推荐）

创建服务文件：
```bash
sudo nano /etc/systemd/system/instrument-detection-api.service
```

添加以下内容（修改路径为你的实际路径）：
```ini
[Unit]
Description=Instrument Defect Detection API
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/project/BlesstringYolo/backend
Environment="PATH=/path/to/project/BlesstringYolo/backend/venv/bin"
ExecStart=/path/to/project/BlesstringYolo/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable instrument-detection-api
sudo systemctl start instrument-detection-api
sudo systemctl status instrument-detection-api
```

## 🌐 步骤3: 部署前端服务

### 3.1 进入前端目录
```bash
cd /path/to/project/BlesstringYolo/frontend
```

### 3.2 安装Node依赖
```bash
npm install
```

### 3.3 配置API地址

编辑 `src/services/api.js`，修改API基础URL：
```javascript
const API_BASE_URL = 'http://your-server-ip:8000/api/v1'
```

### 3.4 构建生产版本
```bash
npm run build
```

### 3.5 使用Nginx部署前端（推荐）

安装Nginx：
```bash
sudo apt install nginx -y
```

创建Nginx配置：
```bash
sudo nano /etc/nginx/sites-available/instrument-detection
```

添加以下内容：
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 或服务器IP

    root /path/to/project/BlesstringYolo/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/instrument-detection /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3.6 开发模式运行（可选）

如果使用开发模式：
```bash
chmod +x start.sh
./start.sh
```

## 🔒 步骤4: 配置防火墙

```bash
# 允许HTTP和HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 如果直接访问API
sudo ufw allow 8000/tcp

# 启用防火墙
sudo ufw enable
```

## 🧪 步骤5: 测试部署

1. **测试后端API**:
   - 访问: http://your-server-ip:8000/docs
   - 测试上传接口: http://your-server-ip:8000/api/v1/upload
   - 测试健康检查: http://your-server-ip:8000/health

2. **测试前端**:
   - 访问: http://your-domain.com 或 http://your-server-ip
   - 尝试上传图片并检测

## 🔄 步骤6: 使用自定义Yolo模型

1. 将训练好的模型文件上传到 `models/` 目录：
```bash
# 例如
scp best.pt user@server:/path/to/project/BlesstringYolo/models/
```

2. 确保文件名为 `best.pt`，系统会自动加载

3. 如果使用其他文件名，修改 `backend/app/config.py` 中的配置

## 📊 监控和日志

### 查看后端日志
```bash
# 如果使用systemd
sudo journalctl -u instrument-detection-api -f

# 或者查看uvicorn日志
tail -f /path/to/logs/app.log
```

### 查看Nginx日志
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🔧 常见问题

### 问题1: 端口被占用
```bash
# 查看端口占用
sudo lsof -i :8000
# 或
sudo netstat -tlnp | grep 8000

# 修改端口（修改start.sh或systemd服务文件）
```

### 问题2: 权限问题
```bash
# 确保uploads目录可写
sudo chmod -R 755 /path/to/project/BlesstringYolo/uploads
sudo chown -R your-username:your-username /path/to/project/BlesstringYolo/uploads
```

### 问题3: CORS错误
修改 `backend/app/main.py` 中的CORS配置，添加前端域名到允许列表。

### 问题4: 模型加载失败
- 检查模型文件路径
- 确认模型文件格式正确
- 查看错误日志

## 🔐 安全建议

1. **生产环境**:
   - 配置HTTPS（使用Let's Encrypt）
   - 限制CORS允许的域名
   - 设置文件上传大小限制
   - 添加API认证

2. **防火墙**:
   - 只开放必要的端口
   - 使用fail2ban防止暴力破解

3. **数据备份**:
   - 定期备份模型文件
   - 备份上传的图片数据

## 📝 下一步

- [ ] 配置HTTPS
- [ ] 集成LabelStudio API
- [ ] 添加用户认证
- [ ] 设置监控告警
- [ ] 配置自动备份

---

**部署完成后，你就可以开始使用乐器瑕疵检测系统了！** 🎸

