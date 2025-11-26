import httpx
from typing import List, Optional, Dict, Any
from app.config import LABEL_STUDIO_URL, LABEL_STUDIO_API_KEY
from app.models.schemas import LabelStudioTask, LabelStudioTaskCreate
from datetime import datetime

class LabelStudioService:
    """LabelStudio API集成服务"""
    
    def __init__(self):
        self.base_url = LABEL_STUDIO_URL.rstrip('/')
        self.api_key = LABEL_STUDIO_API_KEY
        self.api_url = f"{self.base_url}/api"
        self.headers = {
            "Content-Type": "application/json"
        }
        # 如果有API key，添加Authorization头
        if self.api_key:
            self.headers["Authorization"] = f"Token {self.api_key}"
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """获取所有标注项目"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.api_url}/projects/",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json().get("results", [])
            except httpx.HTTPError as e:
                raise Exception(f"获取LabelStudio项目失败: {str(e)}")
    
    async def create_project(self, task_data: LabelStudioTaskCreate) -> Dict[str, Any]:
        """创建新的标注项目"""
        project_data = {
            "title": task_data.title,
            "description": task_data.description or "",
            "label_config": self._get_default_label_config(),
            "input_type": "IMAGE"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.api_url}/projects/",
                    json=project_data,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"创建LabelStudio项目失败: {str(e)}")
    
    async def get_project(self, project_id: int) -> Dict[str, Any]:
        """获取单个项目详情"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.api_url}/projects/{project_id}/",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"获取LabelStudio项目详情失败: {str(e)}")
    
    async def delete_project(self, project_id: int) -> bool:
        """删除标注项目"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.delete(
                    f"{self.api_url}/projects/{project_id}/",
                    headers=self.headers
                )
                response.raise_for_status()
                return True
            except httpx.HTTPError as e:
                raise Exception(f"删除LabelStudio项目失败: {str(e)}")
    
    async def export_project(self, project_id: int, export_type: str = "YOLO") -> bytes:
        """导出标注数据
        
        Args:
            project_id: 项目ID
            export_type: 导出格式 (YOLO, JSON, COCO等)
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.get(
                    f"{self.api_url}/projects/{project_id}/export",
                    params={"exportType": export_type},
                    headers=self.headers
                )
                response.raise_for_status()
                return response.content
            except httpx.HTTPError as e:
                raise Exception(f"导出LabelStudio项目数据失败: {str(e)}")
    
    async def import_tasks(self, project_id: int, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """导入任务到项目"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.api_url}/projects/{project_id}/import",
                    json=tasks,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"导入任务到LabelStudio项目失败: {str(e)}")
    
    def get_project_url(self, project_id: int) -> str:
        """获取项目访问URL"""
        return f"{self.base_url}/projects/{project_id}/"
    
    def get_task_url(self, project_id: int, task_id: int) -> str:
        """获取任务标注URL"""
        return f"{self.base_url}/projects/{project_id}/tasks/{task_id}/"
    
    def _get_default_label_config(self) -> str:
        """获取默认的标注配置（YOLO格式的边界框）"""
        return """<View>
  <Image name="image" value="$image"/>
  <RectangleLabels name="label" toName="image">
    <Label value="scratch" background="red"/>
    <Label value="dent" background="blue"/>
    <Label value="crack" background="green"/>
    <Label value="stain" background="yellow"/>
  </RectangleLabels>
</View>"""
    
    async def convert_to_labelstudio_tasks(self, project_data: Dict[str, Any]) -> LabelStudioTask:
        """将LabelStudio项目数据转换为内部Task模型"""
        created_at = None
        if project_data.get("created_at"):
            try:
                # 处理不同的时间格式
                created_str = project_data["created_at"].replace("Z", "+00:00")
                created_at = datetime.fromisoformat(created_str)
            except Exception:
                pass
        
        return LabelStudioTask(
            id=project_data.get("id"),
            title=project_data.get("title", ""),
            description=project_data.get("description"),
            created_at=created_at,
            url=self.get_project_url(project_data.get("id", 0))
        )

