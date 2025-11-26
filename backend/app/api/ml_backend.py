"""
LabelStudio ML Backend API
实现LabelStudio ML后端接口，用于自动预标注
"""
from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any, Optional
import base64
import httpx
import aiofiles
from pathlib import Path
from app.config import UPLOAD_DIR

router = APIRouter(tags=["LabelStudio ML Backend"])

@router.get("/health")
async def ml_backend_health():
    """ML后端健康检查"""
    return {"status": "UP"}

@router.post("/predict")
async def predict(request: Request):
    """
    LabelStudio ML后端预测接口
    接收LabelStudio格式的请求，返回预标注结果
    """
    try:
        body = await request.json()
        
        # LabelStudio请求格式:
        # {
        #   "tasks": [{
        #     "id": 1,
        #     "data": {
        #       "image": "url或base64数据"
        #     }
        #   }],
        #   "model_version": "v1"
        # }
        
        tasks = body.get("tasks", [])
        if not tasks:
            raise HTTPException(status_code=400, detail="No tasks provided")
        
        results = []
        
        for task in tasks:
            task_id = task.get("id")
            task_data = task.get("data", {})
            
            # 获取图片数据
            image_url = task_data.get("image")
            if not image_url:
                continue
            
            # 下载或读取图片
            image_path = await _get_image_path(image_url)
            
            # 执行分割
            try:
                from app.services.yolo_service import YoloService
                from app.models.schemas import SegmentResult
                segment_result = YoloService.segment(str(image_path))
                
                # 转换为LabelStudio格式
                labelstudio_result = _convert_to_labelstudio_format(segment_result, task_id)
                results.append(labelstudio_result)
            except Exception as e:
                # 如果分割失败，返回空结果
                results.append({
                    "result": [],
                    "score": 0.0
                })
        
        return {"results": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def _get_image_path(image_url: str) -> Path:
    """获取图片路径，支持URL和base64"""
    import uuid
    
    # 如果是base64数据
    if image_url.startswith("data:image"):
        # data:image/png;base64,iVBORw0KG...
        header, data = image_url.split(",", 1)
        image_data = base64.b64decode(data)
        
        # 保存到临时文件（异步）
        temp_filename = f"{uuid.uuid4()}.png"
        temp_path = UPLOAD_DIR / temp_filename
        async with aiofiles.open(temp_path, "wb") as f:
            await f.write(image_data)
        return temp_path
    
    # 如果是URL
    if image_url.startswith("http"):
        # 下载图片
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url, timeout=30.0)
            response.raise_for_status()
            
            temp_filename = f"{uuid.uuid4()}.jpg"
            temp_path = UPLOAD_DIR / temp_filename
            async with aiofiles.open(temp_path, "wb") as f:
                await f.write(response.content)
            return temp_path
    
    # 如果是本地路径
    if Path(image_url).exists():
        return Path(image_url)
    
    raise ValueError(f"无法处理图片URL: {image_url}")

def _convert_to_labelstudio_format(segment_result, task_id: Optional[int] = None) -> Dict[str, Any]:
    """
    将分割结果转换为LabelStudio格式
    
    LabelStudio格式:
    {
      "result": [{
        "from_name": "label",
        "to_name": "image",
        "type": "brushlabels",
        "value": {
          "brushlabels": ["scratch"],
          "format": "rle",
          "rle": [...]  # RLE编码的mask
        }
      }],
      "score": 0.95
    }
    
    或者使用polygon格式:
    {
      "result": [{
        "from_name": "label",
        "to_name": "image",
        "type": "polygonlabels",
        "value": {
          "polygonlabels": ["scratch"],
          "points": [[x1, y1], [x2, y2], ...]
        }
      }],
      "score": 0.95
    }
    """
    result_items = []
    
    for mask in segment_result.masks:
        # 使用polygon格式（更简单，不需要RLE编码）
        polygon_points = [[point.x, point.y] for point in mask.polygon]
        
        result_item = {
            "from_name": "label",
            "to_name": "image",
            "type": "polygonlabels",
            "value": {
                "polygonlabels": [mask.class_name],
                "points": polygon_points
            },
            "score": mask.confidence
        }
        result_items.append(result_item)
    
    # 计算平均置信度
    avg_score = sum(m.confidence for m in segment_result.masks) / len(segment_result.masks) if segment_result.masks else 0.0
    
    return {
        "result": result_items,
        "score": avg_score
    }

@router.post("/setup")
async def setup():
    """ML后端设置接口"""
    return {
        "model_version": "v1",
        "status": "ok"
    }

