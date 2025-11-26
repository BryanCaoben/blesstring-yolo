from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services import file_service
from app.models.schemas import UploadResponse

router = APIRouter(tags=["文件上传"])

@router.post("/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """上传图片文件"""
    try:
        file_path = await file_service.save_uploaded_file(file)
        file_url = file_service.get_file_url(file_path)
        
        return UploadResponse(
            filename=file.filename,
            file_path=str(file_path),
            message="上传成功"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

