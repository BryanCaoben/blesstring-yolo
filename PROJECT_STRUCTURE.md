# 📁 项目结构说明

## 完整目录树

```
BlesstringYolo/
│
├── 📄 README.md                    # 项目主说明文档
├── 📄 QUICKSTART.md                # 快速开始指南
├── 📄 DEPLOYMENT.md                # 详细部署指南
├── 📄 PROJECT_STRUCTURE.md         # 本文件 - 项目结构说明
├── 📄 .gitignore                   # Git忽略文件配置
│
├── 📂 backend/                     # 后端FastAPI项目
│   ├── 📄 requirements.txt         # Python依赖包列表
│   ├── 📄 README.md                # 后端说明文档
│   ├── 📄 start.sh                 # Linux/Mac启动脚本
│   ├── 📄 start.bat                # Windows启动脚本
│   ├── 📄 .env.example             # 环境变量示例（需手动创建）
│   │
│   └── 📂 app/                     # 应用主目录
│       ├── 📄 __init__.py          # Python包初始化
│       ├── 📄 main.py              # FastAPI应用入口
│       ├── 📄 config.py            # 配置文件
│       │
│       ├── 📂 api/                 # API路由层
│       │   ├── 📄 __init__.py
│       │   ├── 📄 upload.py        # 文件上传接口
│       │   └── 📄 detection.py     # 瑕疵检测接口
│       │
│       ├── 📂 models/              # 数据模型层
│       │   ├── 📄 __init__.py
│       │   └── 📄 schemas.py       # Pydantic数据模型
│       │
│       └── 📂 services/            # 业务逻辑层
│           ├── 📄 __init__.py
│           ├── 📄 file_service.py  # 文件处理服务
│           └── 📄 yolo_service.py  # Yolo模型调用服务
│
├── 📂 frontend/                    # 前端React项目
│   ├── 📄 package.json             # Node.js依赖配置
│   ├── 📄 vite.config.js           # Vite构建配置
│   ├── 📄 index.html               # HTML入口文件
│   ├── 📄 README.md                # 前端说明文档
│   ├── 📄 start.sh                 # 启动脚本
│   │
│   └── 📂 src/                     # 源代码目录
│       ├── 📄 main.jsx             # React应用入口
│       ├── 📄 App.jsx              # 主应用组件
│       ├── 📄 App.css              # 应用样式
│       ├── 📄 index.css            # 全局样式
│       │
│       ├── 📂 components/          # React组件
│       │   ├── 📂 ImageUpload/     # 图片上传组件
│       │   │   └── 📄 index.jsx
│       │   └── 📂 DetectionResult/ # 检测结果展示组件
│       │       └── 📄 index.jsx
│       │
│       ├── 📂 services/            # API服务层
│       │   └── 📄 api.js           # API调用封装
│       │
│       └── 📂 utils/               # 工具函数（预留）
│
├── 📂 models/                      # 模型文件目录
│   └── 📄 .gitkeep                 # 保持目录结构（不提交模型文件）
│
└── 📂 uploads/                     # 上传文件目录
    └── 📄 .gitkeep                 # 保持目录结构（不提交上传文件）
```

## 📋 关键文件说明

### 后端关键文件

| 文件 | 说明 |
|------|------|
| `app/main.py` | FastAPI应用主入口，配置路由、中间件等 |
| `app/config.py` | 应用配置，包含路径、环境变量等 |
| `app/api/upload.py` | 处理图片上传的API端点 |
| `app/api/detection.py` | 处理瑕疵检测的API端点 |
| `app/services/yolo_service.py` | Yolo模型调用服务，单例模式管理模型 |
| `app/services/file_service.py` | 文件处理服务，处理上传和保存 |
| `app/models/schemas.py` | 数据模型定义，使用Pydantic验证 |

### 前端关键文件

| 文件 | 说明 |
|------|------|
| `src/App.jsx` | 主应用组件，包含页面布局和状态管理 |
| `src/main.jsx` | React应用入口，配置Ant Design |
| `src/components/ImageUpload/index.jsx` | 图片上传组件，支持拖拽 |
| `src/components/DetectionResult/index.jsx` | 检测结果展示组件，Canvas绘制 |
| `src/services/api.js` | API调用封装，使用Axios |

## 🔄 数据流向

```
用户上传图片
    ↓
前端 ImageUpload 组件
    ↓
POST /api/v1/upload
    ↓
后端 upload.py 处理
    ↓
file_service.py 保存文件
    ↓
返回文件路径
    ↓
前端调用检测接口
    ↓
POST /api/v1/detect
    ↓
后端 detection.py 处理
    ↓
yolo_service.py 调用Yolo模型
    ↓
返回检测结果
    ↓
前端 DetectionResult 组件展示
```

## 🗂️ 目录职责

### backend/
- **职责**: 提供RESTful API服务
- **技术**: FastAPI, Uvicorn, Ultralytics
- **功能**: 文件上传、瑕疵检测、静态文件服务

### frontend/
- **职责**: 提供用户交互界面
- **技术**: React, Ant Design, Vite, Axios
- **功能**: 图片上传、检测触发、结果可视化

### models/
- **职责**: 存储AI模型文件
- **内容**: YoloV8模型文件（.pt格式）
- **注意**: 大文件不上传Git，需手动部署

### uploads/
- **职责**: 存储用户上传的图片
- **访问**: 通过 `/static/{filename}` URL访问
- **注意**: 生产环境需要定期清理

## 📝 扩展建议

### 添加新功能时的文件位置

1. **新的API接口**: 在 `backend/app/api/` 创建新文件
2. **新的业务逻辑**: 在 `backend/app/services/` 创建新服务
3. **新的前端组件**: 在 `frontend/src/components/` 创建新目录
4. **新的工具函数**: 在 `frontend/src/utils/` 添加文件

### 集成LabelStudio时的结构

建议创建：
- `backend/app/services/labelstudio_service.py` - LabelStudio API调用
- `backend/app/api/labelstudio.py` - LabelStudio相关接口
- `frontend/src/components/LabelStudioView/` - LabelStudio集成组件

---

**了解项目结构有助于更好地开发和维护！** 📚

