from fastapi import APIRouter, HTTPException
from typing import List
from app.services.labelstudio_service import LabelStudioService
from app.models.schemas import (
    LabelStudioTask, 
    LabelStudioTaskCreate, 
    LabelStudioTaskResponse
)

router = APIRouter(tags=["标注管理"])
service = LabelStudioService()

@router.get("/projects", response_model=LabelStudioTaskResponse)
async def list_projects():
    """获取所有标注项目"""
    try:
        projects_data = await service.get_projects()
        tasks = []
        for project in projects_data:
            task = await service.convert_to_labelstudio_tasks(project)
            tasks.append(task)
        
        return LabelStudioTaskResponse(
            success=True,
            tasks=tasks
        )
    except Exception as e:
        return LabelStudioTaskResponse(
            success=False,
            error=str(e)
        )

@router.post("/projects", response_model=LabelStudioTaskResponse)
async def create_project(task_data: LabelStudioTaskCreate):
    """创建新的标注项目"""
    try:
        project_data = await service.create_project(task_data)
        task = await service.convert_to_labelstudio_tasks(project_data)
        
        return LabelStudioTaskResponse(
            success=True,
            task=task
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}", response_model=LabelStudioTaskResponse)
async def get_project(project_id: int):
    """获取项目详情"""
    try:
        project_data = await service.get_project(project_id)
        task = await service.convert_to_labelstudio_tasks(project_data)
        
        return LabelStudioTaskResponse(
            success=True,
            task=task
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/projects/{project_id}")
async def delete_project(project_id: int):
    """删除标注项目"""
    try:
        await service.delete_project(project_id)
        return {"success": True, "message": "项目已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/export")
async def export_project(project_id: int, export_type: str = "YOLO"):
    """导出标注数据"""
    try:
        data = await service.export_project(project_id, export_type)
        from fastapi.responses import Response
        return Response(
            content=data,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=project_{project_id}_{export_type}.zip"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/url")
async def get_project_url(project_id: int):
    """获取项目访问URL"""
    try:
        url = service.get_project_url(project_id)
        return {"success": True, "url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

