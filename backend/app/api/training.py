from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from pathlib import Path
from app.services.training_service import TrainingService
from app.models.schemas import (
    TrainingTask,
    TrainingTaskCreate,
    TrainingTaskResponse,
    TrainingConfig
)
from app.config import TRAINING_DATA_DIR
import aiofiles
from datetime import datetime

router = APIRouter(tags=["训练管理"])
service = TrainingService()

@router.get("/tasks", response_model=TrainingTaskResponse)
async def list_tasks():
    """获取所有训练任务"""
    try:
        tasks = service.list_tasks()
        return TrainingTaskResponse(
            success=True,
            tasks=tasks
        )
    except Exception as e:
        return TrainingTaskResponse(
            success=False,
            error=str(e)
        )

@router.get("/tasks/{task_id}", response_model=TrainingTaskResponse)
async def get_task(task_id: str):
    """获取训练任务详情"""
    try:
        task = service.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="训练任务不存在")
        
        return TrainingTaskResponse(
            success=True,
            task=task
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks", response_model=TrainingTaskResponse)
async def create_task(task_create: TrainingTaskCreate):
    """创建训练任务"""
    try:
        task = await service.create_training_task(task_create)
        return TrainingTaskResponse(
            success=True,
            task=task
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/{task_id}/start", response_model=TrainingTaskResponse)
async def start_training(task_id: str):
    """启动训练任务"""
    try:
        task = await service.start_training(task_id)
        return TrainingTaskResponse(
            success=True,
            task=task
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/{task_id}/stop")
async def stop_training(task_id: str):
    """停止训练任务"""
    try:
        success = await service.stop_training(task_id)
        if success:
            return {"success": True, "message": "训练任务已停止"}
        else:
            raise HTTPException(status_code=404, detail="训练任务不存在或未在运行")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """删除训练任务"""
    try:
        success = await service.delete_task(task_id)
        if success:
            return {"success": True, "message": "训练任务已删除"}
        else:
            raise HTTPException(status_code=404, detail="训练任务不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/datasets/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """上传训练数据集（ZIP格式）"""
    try:
        # 检查文件类型
        if not file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="只支持ZIP格式的数据集")
        
        # 保存文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = TRAINING_DATA_DIR / safe_filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return {
            "success": True,
            "message": "数据集上传成功",
            "filename": safe_filename,
            "path": str(file_path)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

