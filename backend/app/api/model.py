from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from typing import Optional
from pathlib import Path
from app.services.model_service import ModelService
from app.models.schemas import ModelResponse, ModelUpload, ModelMetadata, ModelType
from app.services.yolo_service import YoloService

router = APIRouter(tags=["模型管理"])
service = ModelService()

@router.get("/models", response_model=ModelResponse)
async def list_models():
    """获取所有模型列表"""
    try:
        models = service.list_models()
        return ModelResponse(
            success=True,
            models=models
        )
    except Exception as e:
        return ModelResponse(
            success=False,
            error=str(e)
        )

@router.get("/models/active", response_model=ModelResponse)
async def get_active_model():
    """获取当前激活的模型"""
    try:
        model = service.get_active_model()
        if not model:
            return ModelResponse(
                success=False,
                error="没有激活的模型"
            )
        return ModelResponse(
            success=True,
            model=model
        )
    except Exception as e:
        return ModelResponse(
            success=False,
            error=str(e)
        )

@router.get("/models/{model_id}", response_model=ModelResponse)
async def get_model(model_id: str):
    """获取模型详情"""
    try:
        model = service.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="模型不存在")
        
        return ModelResponse(
            success=True,
            model=model
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/models/upload", response_model=ModelResponse)
async def upload_model(
    file: UploadFile = File(...),
    name: str = None,
    description: Optional[str] = None,
    training_task_id: Optional[str] = None,
    model_type: str = "detection"
):
    """上传模型文件"""
    try:
        if not name:
            # 如果没有提供名称，使用文件名（去掉扩展名）
            name = Path(file.filename).stem
        
        # 解析模型类型
        model_type_enum = ModelType.DETECTION
        if model_type.lower() == "segmentation" or model_type.lower() == "seg":
            model_type_enum = ModelType.SEGMENTATION
        
        model = await service.upload_model(
            file=file,
            name=name,
            description=description,
            training_task_id=training_task_id,
            model_type=model_type_enum
        )
        
        return ModelResponse(
            success=True,
            model=model
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@router.post("/models/{model_id}/activate")
async def activate_model(model_id: str):
    """激活模型（设置为当前使用的模型）"""
    try:
        success = await service.set_active_model(model_id)
        if success:
            # 清除YoloService的缓存，强制重新加载模型
            YoloService._model = None
            return {"success": True, "message": "模型已激活"}
        else:
            raise HTTPException(status_code=404, detail="模型不存在或文件不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/models/{model_id}")
async def delete_model(model_id: str):
    """删除模型"""
    try:
        success = await service.delete_model(model_id)
        if success:
            return {"success": True, "message": "模型已删除"}
        else:
            raise HTTPException(status_code=404, detail="模型不存在")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/{model_id}/download")
async def download_model(model_id: str):
    """下载模型文件"""
    try:
        file_path = service.get_model_file_path(model_id)
        if not file_path:
            raise HTTPException(status_code=404, detail="模型文件不存在")
        
        model = service.get_model(model_id)
        return FileResponse(
            path=str(file_path),
            filename=model.filename,
            media_type="application/octet-stream"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/models/{model_id}", response_model=ModelResponse)
async def update_model_metadata(
    model_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    accuracy: Optional[float] = None,
    precision: Optional[float] = None,
    recall: Optional[float] = None,
    mAP: Optional[float] = None,
    version: Optional[str] = None
):
    """更新模型元数据"""
    try:
        kwargs = {}
        if name is not None:
            kwargs['name'] = name
        if description is not None:
            kwargs['description'] = description
        if accuracy is not None:
            kwargs['accuracy'] = accuracy
        if precision is not None:
            kwargs['precision'] = precision
        if recall is not None:
            kwargs['recall'] = recall
        if mAP is not None:
            kwargs['mAP'] = mAP
        if version is not None:
            kwargs['version'] = version
        
        model = await service.update_model_metadata(model_id, **kwargs)
        if not model:
            raise HTTPException(status_code=404, detail="模型不存在")
        
        return ModelResponse(
            success=True,
            model=model
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

