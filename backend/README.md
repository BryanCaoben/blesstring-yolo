# 后端服务说明

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── config.py            # 配置文件
│   ├── api/                 # API路由
│   │   ├── __init__.py
│   │   ├── upload.py        # 文件上传接口
│   │   └── detection.py     # 瑕疵检测接口
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic模型定义
│   └── services/            # 业务逻辑层
│       ├── __init__.py
│       ├── file_service.py  # 文件处理服务
│       └── yolo_service.py  # Yolo模型调用服务
└── requirements.txt         # Python依赖包
```

## 启动服务

### 开发模式（自动重载）

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 生产模式

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 环境变量

创建 `.env` 文件（参考 `.env.example`）：

```env
LABEL_STUDIO_URL=http://localhost:8080
LABEL_STUDIO_API_KEY=your_api_key
YOLO_MODEL_PATH=yolov8n.pt
```

## 主要功能模块

### 1. 文件上传服务 (`file_service.py`)
- 文件类型验证
- 异步文件保存
- 唯一文件名生成

### 2. Yolo检测服务 (`yolo_service.py`)
- 模型单例管理
- 自动加载自定义模型
- 检测结果解析

### 3. API路由
- `/api/v1/upload` - 文件上传
- `/api/v1/detect` - 瑕疵检测
- `/api/v1/detect/{filename}` - 根据文件名检测

## 依赖说明

- **fastapi**: Web框架
- **uvicorn**: ASGI服务器
- **ultralytics**: YoloV8模型
- **pydantic**: 数据验证
- **aiofiles**: 异步文件操作

