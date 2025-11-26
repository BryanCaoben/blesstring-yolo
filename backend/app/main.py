from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config import UPLOAD_DIR
from app.api import detection, upload, labelstudio, training, model
try:
    from app.api import ml_backend
    print("✅ ML后端模块导入成功")
except ImportError as e:
    print(f"⚠️ 警告: ML后端模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    ml_backend = None
except Exception as e:
    print(f"⚠️ 警告: ML后端模块加载出错: {e}")
    import traceback
    traceback.print_exc()
    ml_backend = None

app = FastAPI(
    title="乐器瑕疵检测API",
    description="基于YoloV8的乐器瑕疵检测服务 - 一体化标注训练模型管理平台",
    version="2.0.0"
)

# 配置CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务（用于访问上传的图片）
app.mount("/static", StaticFiles(directory=str(UPLOAD_DIR)), name="static")

# 注册路由
app.include_router(upload.router, prefix="/api/v1")
app.include_router(detection.router, prefix="/api/v1")
app.include_router(labelstudio.router, prefix="/api/v1")
app.include_router(training.router, prefix="/api/v1")
app.include_router(model.router, prefix="/api/v1")
# LabelStudio ML后端路由
if ml_backend is not None:
    app.include_router(ml_backend.router, prefix="/api/v1/ml")
    print("✅ ML后端路由注册成功: /api/v1/ml/*")
else:
    print("❌ 警告: ML后端路由未注册，请检查ml_backend模块导入")

@app.get("/")
async def root():
    return {"message": "乐器瑕疵检测API服务", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

