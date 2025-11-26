"""
LabelStudio ML Backend API
实现LabelStudio ML后端接口，用于自动预标注
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
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
    import traceback
    import logging
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        body = await request.json()
        print(f"[ML Backend] 收到预测请求: {body}")  # 也输出到控制台
        logger.info(f"收到预测请求: {body}")
        
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
            logger.warning("没有提供tasks")
            raise HTTPException(status_code=400, detail="No tasks provided")
        
        results = []
        
        for task in tasks:
            task_id = task.get("id")
            task_data = task.get("data", {})
            
            # 获取图片数据
            image_url = task_data.get("image")
            if not image_url:
                logger.warning(f"Task {task_id} 没有图片URL")
                # 返回空结果而不是跳过
                results.append({
                    "result": [],
                    "score": 0.0
                })
                continue
            
            logger.info(f"处理Task {task_id}, 图片URL: {image_url[:100]}...")
            
            # 下载或读取图片
            try:
                image_path = await _get_image_path(image_url)
                logger.info(f"图片已下载/读取: {image_path}")
            except Exception as e:
                logger.error(f"获取图片失败: {e}")
                traceback.print_exc()
                results.append({
                    "result": [],
                    "score": 0.0
                })
                continue
            
            # 执行分割
            try:
                from app.services.yolo_service import YoloService
                from app.models.schemas import SegmentResult
                
                logger.info(f"开始执行分割: {image_path}")
                segment_result = YoloService.segment(str(image_path))
                logger.info(f"分割完成，找到 {len(segment_result.masks)} 个mask")
                
                # 转换为LabelStudio格式
                labelstudio_result = _convert_to_labelstudio_format(segment_result, task_id)
                logger.info(f"转换完成，结果: {len(labelstudio_result.get('result', []))} 个标注")
                results.append(labelstudio_result)
            except Exception as e:
                logger.error(f"分割失败: {e}")
                traceback.print_exc()
                # 如果分割失败，返回空结果（但不是空数组）
                results.append({
                    "result": [],
                    "score": 0.0
                })
        
        # LabelStudio期望返回格式: {"results": [...]}
        # 使用JSONResponse确保返回正确的格式
        logger.info(f"返回预测结果: {len(results)} 个任务结果")
        response_data = {"results": results}
        print(f"[ML Backend] 返回响应: {response_data}")  # 调试输出
        return JSONResponse(content=response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"预测请求处理失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

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
    
    LabelStudio期望的格式:
    {
      "result": [{
        "from_name": "label",  # 必须与标注配置中的from_name匹配
        "to_name": "image",    # 必须与标注配置中的to_name匹配
        "type": "polygonlabels",
        "value": {
          "polygonlabels": ["scratch"],
          "points": [[x1, y1], [x2, y2], ...]  # 相对坐标 (0-100)
        },
        "score": 0.95
      }],
      "score": 0.95
    }
    """
    result_items = []
    
    if not segment_result or not segment_result.masks:
        # 如果没有检测到任何东西，返回空结果
        return {
            "result": [],
            "score": 0.0
        }
    
    for mask in segment_result.masks:
        # 使用polygon格式（更简单，不需要RLE编码）
        # 确保points是相对坐标 (0-100)，而不是绝对坐标
        polygon_points = []
        
        for point in mask.polygon:
            # 确保坐标是数值类型
            x = float(point.x) if hasattr(point, 'x') else float(point[0])
            y = float(point.y) if hasattr(point, 'y') else float(point[1])
            polygon_points.append([x, y])
        
        # LabelStudio要求至少有3个点才能形成多边形
        if len(polygon_points) < 3:
            continue
        
        result_item = {
            "from_name": "label",  # 这个名称需要与Label Studio项目配置匹配
            "to_name": "image",    # 这个名称需要与Label Studio项目配置匹配
            "type": "polygonlabels",
            "value": {
                "polygonlabels": [mask.class_name] if mask.class_name else ["defect"],
                "points": polygon_points
            },
            "score": float(mask.confidence) if hasattr(mask, 'confidence') else 0.5
        }
        result_items.append(result_item)
    
    # 计算平均置信度
    if segment_result.masks:
        avg_score = sum(getattr(m, 'confidence', 0.5) for m in segment_result.masks) / len(segment_result.masks)
    else:
        avg_score = 0.0
    
    return {
        "result": result_items,
        "score": float(avg_score)
    }

@router.post("/setup")
async def setup():
    """ML后端设置接口"""
    return {
        "model_version": "v1",
        "status": "ok"
    }

