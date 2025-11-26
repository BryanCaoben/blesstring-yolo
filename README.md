# 🎸 乐器瑕疵检测系统

基于 FastAPI + React + YoloV8 的乐器瑕疵检测AI后台服务

## 📋 项目简介

这是一个用于检测二手乐器瑕疵的AI系统，通过用户上传的图片可以自动识别乐器上的瑕疵。系统集成了：

- **后端**: FastAPI - 提供RESTful API服务
- **前端**: React + Ant Design - 现代化用户界面
- **AI模型**: YoloV8 - 目标检测模型
- **标注工具**: LabelStudio - 数据标注（待集成）

## 🏗️ 项目结构

```
BlesstringYolo/
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── main.py         # FastAPI主入口
│   │   ├── config.py       # 配置文件
│   │   ├── api/            # API路由
│   │   ├── models/         # 数据模型
│   │   └── services/       # 业务逻辑
│   └── requirements.txt    # Python依赖
│
├── frontend/               # React前端
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/     # React组件
│   │   └── services/       # API调用
│   └── package.json
│
├── models/                 # 存储训练好的模型文件
└── uploads/                # 存储上传的图片
```

## 🔧 环境要求

### 🖥️ 服务器环境（Ubuntu 24）- 必须

**所有服务在服务器上运行**，需要以下环境：

- Python 3.9+
- Node.js 18+（用于构建前端）
- ✅ **LabelStudio 1.21.0**（已在服务器安装）
- ✅ **ultralytics 8.3.231**（已在服务器安装）

### 💻 开发机环境（Windows）- 可选

**开发机主要用于编写和修改代码**，不需要运行完整服务：

- 代码编辑器（VS Code等）
- Node.js 18+（**仅**用于调试前端UI，可选）
- ❌ **不需要安装 Python、LabelStudio 或 YoloV8**

> 💡 **提示**：推荐的工作流程是在开发机编写代码，然后将代码上传到服务器运行。所有检测功能都在服务器上执行。

## 🚀 快速开始

> ⚠️ **注意**：以下所有部署步骤都在 **Ubuntu 24 服务器** 上执行。开发机（Windows）只用于编写代码，不需要部署服务。

### 1. 后端部署

#### 在Ubuntu服务器上：

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 文件，设置LabelStudio URL和API密钥

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 访问API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 2. 前端部署

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:3000 启动

### 3. 使用自定义模型

如果你有训练好的YoloV8模型：

1. 将模型文件（通常是 `best.pt`）放到 `models/` 目录
2. 系统会自动加载自定义模型，如果没有则使用预训练模型

## 📡 API接口说明

### 1. 上传图片
- **接口**: `POST /api/v1/upload`
- **Content-Type**: `multipart/form-data`
- **请求参数**: 
  - `file`: 图片文件（JPG、PNG、JPEG、BMP）
- **返回示例**:
```json
{
  "filename": "instrument.jpg",
  "file_path": "G:/BlesstringYolo/uploads/20231126_102530_instrument.jpg",
  "message": "上传成功"
}
```

### 2. 检测瑕疵
- **接口**: `POST /api/v1/detect`
- **请求体**:
```json
{
  "image_path": "G:/BlesstringYolo/uploads/20231126_102530_instrument.jpg"
}
```
- **返回示例**:
```json
{
  "success": true,
  "result": {
    "image_path": "...",
    "defects": [
      {
        "x1": 100.5,
        "y1": 200.3,
        "x2": 300.8,
        "y2": 400.2,
        "confidence": 0.95,
        "class_name": "scratch"
      }
    ],
    "timestamp": "2023-11-26T10:25:30"
  }
}
```

### 3. 根据文件名检测
- **接口**: `GET /api/v1/detect/{filename}`
- **示例**: `GET /api/v1/detect/20231126_102530_instrument.jpg`

## 🎨 前端功能

1. **图片上传**: 支持拖拽上传，自动验证文件类型
2. **瑕疵检测**: 一键检测，实时显示结果
3. **结果可视化**: 
   - 在图片上标注瑕疵位置
   - 显示置信度和类别信息
   - 统计检测到的瑕疵数量

## 🔗 LabelStudio集成（待开发）

后续计划集成LabelStudio功能：
- 数据标注管理
- 导出标注数据用于模型训练
- 标注结果回传

## 🛠️ 开发指南

### 后端开发

后端采用分层架构：
- **API层** (`app/api/`): 处理HTTP请求和响应
- **服务层** (`app/services/`): 业务逻辑实现
- **模型层** (`app/models/`): 数据模型定义

### 前端开发

前端使用React函数组件和Hooks：
- 组件化开发，易于维护
- Ant Design提供完整的UI组件库
- Axios处理API调用

## 📝 注意事项

1. **CORS配置**: 生产环境请修改 `backend/app/main.py` 中的CORS设置，限制允许的域名
2. **文件大小**: 默认没有限制上传文件大小，生产环境建议添加限制
3. **模型路径**: 确保模型文件路径正确，系统会自动检测 `models/best.pt`
4. **静态文件**: 上传的图片通过 `/static/{filename}` 访问

## 🔄 后续优化计划

- [ ] 集成LabelStudio API，实现标注数据管理
- [ ] 添加批量检测功能
- [ ] 支持更多图片格式
- [ ] 添加检测历史记录
- [ ] 实现模型热更新
- [ ] 添加用户认证和权限管理
- [ ] 优化检测性能
- [ ] 添加检测结果导出功能

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交Issue和Pull Request！

---

**祝使用愉快！** 🎵

