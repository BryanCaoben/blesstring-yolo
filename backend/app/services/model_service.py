import json
import uuid
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from app.config import MODELS_METADATA_FILE, MODEL_DIR
from app.models.schemas import ModelMetadata, ModelType
from fastapi import UploadFile
import aiofiles

class ModelService:
    """模型管理服务"""
    
    def __init__(self):
        self.metadata_file = MODELS_METADATA_FILE
        self.model_dir = MODEL_DIR
        self.model_dir.mkdir(exist_ok=True)
    
    def _load_metadata(self) -> List[Dict]:
        """加载模型元数据"""
        if not self.metadata_file.exists():
            return []
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    
    def _save_metadata(self, metadata_list: List[Dict]):
        """保存模型元数据"""
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_list, f, ensure_ascii=False, indent=2, default=str)
    
    def _get_active_model_id(self) -> Optional[str]:
        """获取当前激活的模型ID"""
        metadata_list = self._load_metadata()
        for item in metadata_list:
            if item.get("is_active"):
                return item.get("id")
        return None
    
    async def upload_model(self, file: UploadFile, name: str, description: Optional[str] = None, 
                          training_task_id: Optional[str] = None, model_type: ModelType = ModelType.DETECTION) -> ModelMetadata:
        """上传模型文件"""
        # 验证文件扩展名
        if not file.filename.endswith('.pt'):
            raise ValueError("只支持.pt格式的模型文件")
        
        # 生成唯一ID和文件名
        model_id = str(uuid.uuid4())
        safe_filename = f"{model_id}_{file.filename}"
        file_path = self.model_dir / safe_filename
        
        # 保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        file_size = file_path.stat().st_size
        
        # 创建元数据
        model = ModelMetadata(
            id=model_id,
            name=name,
            filename=safe_filename,
            file_path=str(file_path),
            file_size=file_size,
            model_type=model_type,
            description=description,
            training_task_id=training_task_id,
            is_active=False,
            created_at=datetime.now()
        )
        
        # 保存元数据
        metadata_list = self._load_metadata()
        metadata_list.append(model.dict())
        self._save_metadata(metadata_list)
        
        return model
    
    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        """获取模型元数据"""
        metadata_list = self._load_metadata()
        for item in metadata_list:
            if item.get("id") == model_id:
                return ModelMetadata(**item)
        return None
    
    def list_models(self) -> List[ModelMetadata]:
        """列出所有模型"""
        metadata_list = self._load_metadata()
        models = []
        for item in metadata_list:
            try:
                model = ModelMetadata(**item)
                models.append(model)
            except Exception:
                continue
        # 按创建时间倒序排列
        models.sort(key=lambda x: x.created_at, reverse=True)
        return models
    
    def get_active_model(self) -> Optional[ModelMetadata]:
        """获取当前激活的模型"""
        active_id = self._get_active_model_id()
        if active_id:
            return self.get_model(active_id)
        return None
    
    async def set_active_model(self, model_id: str) -> bool:
        """设置激活的模型"""
        model = self.get_model(model_id)
        if not model:
            return False
        
        # 检查文件是否存在
        if not Path(model.file_path).exists():
            return False
        
        # 取消其他模型的激活状态
        metadata_list = self._load_metadata()
        for item in metadata_list:
            item["is_active"] = (item.get("id") == model_id)
        self._save_metadata(metadata_list)
        
        return True
    
    async def delete_model(self, model_id: str) -> bool:
        """删除模型"""
        model = self.get_model(model_id)
        if not model:
            return False
        
        # 如果是激活的模型，不允许删除
        if model.is_active:
            raise ValueError("不能删除当前激活的模型，请先切换其他模型")
        
        # 删除文件
        file_path = Path(model.file_path)
        if file_path.exists():
            file_path.unlink()
        
        # 从元数据中删除
        metadata_list = self._load_metadata()
        metadata_list = [item for item in metadata_list if item.get("id") != model_id]
        self._save_metadata(metadata_list)
        
        return True
    
    async def update_model_metadata(self, model_id: str, **kwargs) -> Optional[ModelMetadata]:
        """更新模型元数据"""
        metadata_list = self._load_metadata()
        for item in metadata_list:
            if item.get("id") == model_id:
                # 更新允许的字段
                allowed_fields = ['name', 'description', 'accuracy', 'precision', 'recall', 'mAP', 
                                'trained_at', 'version']
                for key, value in kwargs.items():
                    if key in allowed_fields:
                        item[key] = value
                
                self._save_metadata(metadata_list)
                return ModelMetadata(**item)
        return None
    
    def get_model_file_path(self, model_id: str) -> Optional[Path]:
        """获取模型文件路径"""
        model = self.get_model(model_id)
        if model:
            path = Path(model.file_path)
            if path.exists():
                return path
        return None

