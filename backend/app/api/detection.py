from fastapi import APIRouter, HTTPException
from app.services import yolo_service
from app.models.schemas import DetectionRequest, DetectionResponse, SegmentResult
from pathlib import Path

router = APIRouter(tags=["瑕疵检测"])

@router.post("/detect", response_model=DetectionResponse)
async def detect_defects(request: DetectionRequest):
    """检测图片中的瑕疵"""
    try:
        image_path = Path(request.image_path)
        if not image_path.exists():
            raise HTTPException(status_code=404, detail="图片文件不存在")
        
        result = yolo_service.YoloService.detect(str(image_path))
        
        return DetectionResponse(
            success=True,
            result=result
        )
    except Exception as e:
        return DetectionResponse(
            success=False,
            error=str(e)
        )

@router.get("/detect/{filename}")
async def detect_by_filename(filename: str):
    """根据文件名检测瑕疵"""
    from app.config import UPLOAD_DIR
    
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    request = DetectionRequest(image_path=str(file_path))
    return await detect_defects(request)

@router.post("/segment")
async def segment_image(request: DetectionRequest):
    """分割图片中的瑕疵"""
    try:
        image_path = Path(request.image_path)
        if not image_path.exists():
            raise HTTPException(status_code=404, detail="图片文件不存在")
        
        result = yolo_service.YoloService.segment(str(image_path))
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/segment/{filename}")
async def segment_by_filename(filename: str):
    """根据文件名分割瑕疵"""
    from app.config import UPLOAD_DIR
    
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    request = DetectionRequest(image_path=str(file_path))
    return await segment_image(request)

