# ⚡ 快速开始指南

这个指南帮助你快速上手项目。

## 🎯 项目概述

这个项目包含：
- **后端**: FastAPI服务，提供API接口
- **前端**: React应用，提供用户界面
- **AI模型**: YoloV8用于瑕疵检测

## 💻 开发机环境说明（Windows）

**重要提示**：
- ⭐ **开发机主要用于编写和修改代码**
- ❌ **不需要在开发机安装 LabelStudio 和 YoloV8**
- ✅ **所有服务最终在 Ubuntu 24 服务器上运行**

### 开发机可选功能

#### 1. 前端开发（推荐，用于调试UI）

如果要在开发机上调试前端UI：

```powershell
# 进入前端目录
cd frontend

# 安装依赖（只需要Node.js）
npm install

# 修改代理配置：编辑 vite.config.js
# 将代理地址改为你的服务器IP：target: 'http://your-server-ip:8000'

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:3000 启动，通过代理连接服务器的后端API。

**注意**：需要修改 `frontend/vite.config.js` 中的代理地址为你的服务器IP：
```javascript
proxy: {
  '/api': {
    target: 'http://your-server-ip:8000',  // 改为服务器地址
    changeOrigin: true
  }
}
```

#### 2. 后端本地测试（可选，不推荐）

如果你**确实需要**在开发机上测试后端功能（需要安装YoloV8，会下载较大文件）：

```powershell
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\activate

# 安装依赖（会包含ultralytics，较大）
pip install -r requirements.txt

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

⚠️ **不推荐**：这会下载YoloV8模型，占用较大空间。建议直接在服务器上测试。

### 推荐工作流程

1. **在开发机上**：编写/修改代码 → 提交/推送到服务器
2. **在服务器上**：部署并运行所有服务

## 🖥️ 服务器部署（Ubuntu 24）- 主要部署方式

**⭐ 这是主要的部署方式，所有服务都在服务器上运行。**

你的服务器已经安装了：
- ✅ LabelStudio 1.21.0
- ✅ ultralytics 8.3.231

详细部署步骤请参考 [DEPLOYMENT.md](./DEPLOYMENT.md)

### 快速部署命令

```bash
# 1. 后端
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 2. 前端
cd frontend
npm install
npm run build
# 然后使用Nginx部署dist目录
```

## 🧪 测试流程

1. **上传图片**: 在前端页面上传一张乐器图片
2. **开始检测**: 点击"开始检测"按钮
3. **查看结果**: 
   - 如果有瑕疵，会在图片上标注位置
   - 显示瑕疵类型和置信度

## 📝 使用自定义模型

1. 将训练好的YoloV8模型文件（通常是`best.pt`）放到 `models/` 目录
2. 系统会自动检测并加载自定义模型
3. 如果没有自定义模型，会使用预训练的YoloV8模型

## 🔧 常见问题

### Q: 开发机需要安装哪些环境？
A: 只需要安装代码编辑器（如VS Code）。如果调试前端UI，需要Node.js。**不需要安装Python、LabelStudio或YoloV8**。

### Q: 后端启动失败？
A: 检查Python版本（需要3.9+），确保所有依赖已安装。**建议在服务器上运行后端**。

### Q: 前端无法连接后端？
A: 检查后端是否在服务器8000端口运行，检查前端代理配置中的服务器IP地址是否正确。

### Q: 检测结果不准确？
A: 使用自定义训练的模型，预训练模型可能不适合乐器瑕疵检测

### Q: 上传的图片无法访问？
A: 检查uploads目录权限，确保静态文件服务正常

## 📚 相关文档

- [完整README](./README.md)
- [部署指南](./DEPLOYMENT.md)
- [后端说明](./backend/README.md)
- [前端说明](./frontend/README.md)

## 🚀 下一步

1. 训练自己的YoloV8模型
2. 集成LabelStudio进行数据标注
3. 添加更多功能（批量检测、历史记录等）

---

**主要部署在服务器，开发机只用于编写代码！** 🎵

