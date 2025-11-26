from pathlib import Path
from fastapi import UploadFile
import aiofiles
from app.config import UPLOAD_DIR, ALLOWED_EXTENSIONS
from datetime import datetime

async def save_uploaded_file(file: UploadFile) -> Path:
    """保存上传的文件"""
    # 验证文件类型
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的文件类型: {file_ext}")
    
    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename
    
    # 异步保存文件
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return file_path

def get_file_url(file_path: Path) -> str:
    """获取文件的访问URL"""
    filename = file_path.name
    return f"/static/{filename}"

