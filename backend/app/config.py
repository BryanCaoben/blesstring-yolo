import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 上传文件配置
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# 模型配置
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

# 数据存储配置
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
TRAINING_HISTORY_FILE = DATA_DIR / "training_history.json"
MODELS_METADATA_FILE = DATA_DIR / "models_metadata.json"

# 训练数据配置
TRAINING_DATA_DIR = BASE_DIR / "training_data"
TRAINING_DATA_DIR.mkdir(exist_ok=True)

# LabelStudio配置
LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL", "http://localhost:8080")
LABEL_STUDIO_API_KEY = os.getenv("LABEL_STUDIO_API_KEY", "")

# Yolo模型路径（如果已有训练好的模型）
YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "yolov8n.pt")
YOLO_SEG_MODEL_PATH = os.getenv("YOLO_SEG_MODEL_PATH", "yolov8n-seg.pt")  # 分割模型路径

# 允许的文件类型
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}

# FastAPI配置
API_PREFIX = "/api/v1"

