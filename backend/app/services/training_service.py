import asyncio
import json
import uuid
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
from ultralytics import YOLO
from app.config import TRAINING_HISTORY_FILE, MODEL_DIR, TRAINING_DATA_DIR
from app.models.schemas import TrainingTask, TrainingTaskCreate, TrainingStatus, TrainingConfig

class TrainingService:
    """训练任务管理服务"""
    
    def __init__(self):
        self.history_file = TRAINING_HISTORY_FILE
        self.model_dir = MODEL_DIR
        self.training_data_dir = TRAINING_DATA_DIR
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.tasks_status: Dict[str, TrainingTask] = {}
    
    def _load_history(self) -> List[Dict]:
        """加载训练历史"""
        if not self.history_file.exists():
            return []
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    
    def _save_history(self, history: List[Dict]):
        """保存训练历史"""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2, default=str)
    
    def _save_task(self, task: TrainingTask):
        """保存单个任务到历史"""
        history = self._load_history()
        # 查找是否已存在
        existing_index = None
        for i, item in enumerate(history):
            if item.get("id") == task.id:
                existing_index = i
                break
        
        task_dict = task.dict()
        if existing_index is not None:
            history[existing_index] = task_dict
        else:
            history.append(task_dict)
        
        self._save_history(history)
        self.tasks_status[task.id] = task
    
    def get_task(self, task_id: str) -> Optional[TrainingTask]:
        """获取训练任务"""
        # 先从内存中获取
        if task_id in self.tasks_status:
            return self.tasks_status[task_id]
        
        # 从历史文件中加载
        history = self._load_history()
        for item in history:
            if item.get("id") == task_id:
                return TrainingTask(**item)
        return None
    
    def list_tasks(self) -> List[TrainingTask]:
        """列出所有训练任务"""
        history = self._load_history()
        tasks = []
        for item in history:
            try:
                task = TrainingTask(**item)
                tasks.append(task)
                # 更新内存中的状态
                self.tasks_status[task.id] = task
            except Exception:
                continue
        # 按创建时间倒序排列
        tasks.sort(key=lambda x: x.created_at, reverse=True)
        return tasks
    
    async def create_training_task(self, task_create: TrainingTaskCreate) -> TrainingTask:
        """创建训练任务"""
        task_id = str(uuid.uuid4())
        config = task_create.config or TrainingConfig()
        
        task = TrainingTask(
            id=task_id,
            name=task_create.name,
            dataset_path=task_create.dataset_path,
            status=TrainingStatus.PENDING,
            config=config,
            created_at=datetime.now(),
            total_epochs=config.epochs
        )
        
        self._save_task(task)
        return task
    
    async def start_training(self, task_id: str) -> TrainingTask:
        """启动训练任务"""
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"训练任务 {task_id} 不存在")
        
        if task.status == TrainingStatus.RUNNING:
            raise ValueError(f"训练任务 {task_id} 正在运行中")
        
        if task.status == TrainingStatus.COMPLETED:
            raise ValueError(f"训练任务 {task_id} 已完成")
        
        # 检查数据集路径
        dataset_path = Path(task.dataset_path)
        if not dataset_path.exists():
            raise ValueError(f"数据集路径不存在: {task.dataset_path}")
        
        # 更新任务状态
        task.status = TrainingStatus.RUNNING
        task.started_at = datetime.now()
        task.progress = 0.0
        task.current_epoch = 0
        self._save_task(task)
        
        # 启动异步训练任务
        training_task = asyncio.create_task(self._run_training(task))
        self.running_tasks[task_id] = training_task
        
        return task
    
    async def _run_training(self, task: TrainingTask):
        """执行训练任务（在后台线程中运行）"""
        try:
            # 在事件循环中运行阻塞的YOLO训练
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._train_model, task)
        except Exception as e:
            task.status = TrainingStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            self._save_task(task)
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
    
    def _train_model(self, task: TrainingTask):
        """实际执行YOLO训练（阻塞操作）"""
        try:
            dataset_path = task.dataset_path
            config = task.config
            
            # 加载预训练模型或从头开始
            model = YOLO("yolov8n.pt")  # 使用nano模型作为起点
            
            # 训练回调函数用于更新进度
            def on_train_epoch_end(trainer):
                epoch = trainer.epoch + 1
                total_epochs = trainer.epochs
                task.current_epoch = epoch
                task.progress = (epoch / total_epochs) * 100
                
                # 获取训练指标
                metrics = trainer.metrics if hasattr(trainer, 'metrics') else {}
                task.metrics = {
                    "train_loss": metrics.get("train/box_loss", 0),
                    "train_cls_loss": metrics.get("train/cls_loss", 0),
                    "val_loss": metrics.get("val/box_loss", 0),
                    "val_cls_loss": metrics.get("val/cls_loss", 0),
                    "mAP50": metrics.get("metrics/mAP50(B)", 0),
                    "mAP50-95": metrics.get("metrics/mAP50-95(B)", 0),
                }
                
                # 保存进度
                self._save_task(task)
            
            # 执行训练
            results = model.train(
                data=str(dataset_path) if Path(dataset_path).is_file() else dataset_path,
                epochs=config.epochs,
                batch=config.batch_size,
                imgsz=config.img_size,
                lr0=config.learning_rate,
                device=config.device,
                project=str(self.model_dir),
                name=task.name.replace(" ", "_"),
                exist_ok=True,
            )
            
            # 训练完成
            task.status = TrainingStatus.COMPLETED
            task.completed_at = datetime.now()
            task.progress = 100.0
            task.current_epoch = config.epochs
            
            # 保存模型路径
            model_path = self.model_dir / task.name.replace(" ", "_") / "weights" / "best.pt"
            if model_path.exists():
                task.model_path = str(model_path)
            
            # 保存最终指标
            if hasattr(results, 'results_dict'):
                task.metrics = {
                    "mAP50": results.results_dict.get("metrics/mAP50(B)", 0),
                    "mAP50-95": results.results_dict.get("metrics/mAP50-95(B)", 0),
                }
            
            self._save_task(task)
            
        except Exception as e:
            task.status = TrainingStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            self._save_task(task)
            raise
        finally:
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
    
    async def stop_training(self, task_id: str) -> bool:
        """停止训练任务"""
        if task_id not in self.running_tasks:
            return False
        
        task = self.get_task(task_id)
        if not task:
            return False
        
        # 取消任务
        training_task = self.running_tasks[task_id]
        training_task.cancel()
        
        # 更新状态
        task.status = TrainingStatus.STOPPED
        task.completed_at = datetime.now()
        self._save_task(task)
        
        del self.running_tasks[task_id]
        return True
    
    async def delete_task(self, task_id: str) -> bool:
        """删除训练任务"""
        # 如果任务正在运行，先停止
        if task_id in self.running_tasks:
            await self.stop_training(task_id)
        
        # 从历史中删除
        history = self._load_history()
        history = [item for item in history if item.get("id") != task_id]
        self._save_history(history)
        
        # 从内存中删除
        self.tasks_status.pop(task_id, None)
        
        return True

