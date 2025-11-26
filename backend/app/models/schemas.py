from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DetectionRequest(BaseModel):
    image_path: str
    
class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_name: str

# 分割相关模型
class PolygonPoint(BaseModel):
    x: float
    y: float

class SegmentMask(BaseModel):
    """分割mask，包含多边形点集和边界框"""
    polygon: List[PolygonPoint]  # 多边形点集
    bbox: BoundingBox  # 边界框
    confidence: float
    class_name: str

class SegmentResult(BaseModel):
    """分割结果"""
    image_path: str
    masks: List[SegmentMask]
    timestamp: datetime

class DetectionResult(BaseModel):
    image_path: str
    defects: List[BoundingBox]
    timestamp: datetime

class UploadResponse(BaseModel):
    filename: str
    file_path: str
    message: str

class DetectionResponse(BaseModel):
    success: bool
    result: Optional[DetectionResult] = None
    error: Optional[str] = None

# LabelStudio相关模型
class LabelStudioTask(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    url: Optional[str] = None

class LabelStudioTaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

class LabelStudioTaskResponse(BaseModel):
    success: bool
    task: Optional[LabelStudioTask] = None
    tasks: Optional[List[LabelStudioTask]] = None
    error: Optional[str] = None

# 训练相关模型
class TrainingStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"

class TrainingConfig(BaseModel):
    epochs: int = 100
    batch_size: int = 16
    img_size: int = 640
    learning_rate: float = 0.01
    device: str = "cpu"  # cpu or cuda

class TrainingTask(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    id: str
    name: str
    dataset_path: str
    status: TrainingStatus
    config: TrainingConfig
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0  # 0-100
    current_epoch: int = 0
    total_epochs: int = 0
    metrics: Optional[Dict[str, Any]] = None
    model_path: Optional[str] = None
    error: Optional[str] = None

class TrainingTaskCreate(BaseModel):
    name: str
    dataset_path: str
    config: Optional[TrainingConfig] = None

class TrainingTaskResponse(BaseModel):
    success: bool
    task: Optional[TrainingTask] = None
    tasks: Optional[List[TrainingTask]] = None
    error: Optional[str] = None

# 模型管理相关模型
class ModelType(str, Enum):
    DETECTION = "detection"  # 检测模型
    SEGMENTATION = "segmentation"  # 分割模型

class ModelMetadata(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    id: str
    name: str
    filename: str
    file_path: str
    file_size: int  # bytes
    model_type: ModelType = ModelType.DETECTION  # 模型类型
    version: Optional[str] = None
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    mAP: Optional[float] = None
    trained_at: Optional[datetime] = None
    training_task_id: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = False
    created_at: datetime

class ModelUpload(BaseModel):
    name: str
    description: Optional[str] = None
    training_task_id: Optional[str] = None

class ModelResponse(BaseModel):
    success: bool
    model: Optional[ModelMetadata] = None
    models: Optional[List[ModelMetadata]] = None
    error: Optional[str] = None

