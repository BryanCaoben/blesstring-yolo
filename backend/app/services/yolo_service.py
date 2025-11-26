from ultralytics import YOLO
from pathlib import Path
import numpy as np
import cv2
from app.config import YOLO_MODEL_PATH, YOLO_SEG_MODEL_PATH, MODEL_DIR
from app.models.schemas import DetectionResult, BoundingBox, SegmentResult, SegmentMask, PolygonPoint
from datetime import datetime
from typing import List, Optional

class YoloService:
    _model: Optional[YOLO] = None
    _seg_model: Optional[YOLO] = None
    
    @classmethod
    def get_model(cls):
        """单例模式获取检测模型"""
        if cls._model is None:
            # 尝试加载自定义模型，如果没有则使用预训练模型
            custom_model = MODEL_DIR / "best.pt"
            if custom_model.exists():
                cls._model = YOLO(str(custom_model))
            else:
                cls._model = YOLO(YOLO_MODEL_PATH)
        return cls._model
    
    @classmethod
    def get_segmentation_model(cls):
        """单例模式获取分割模型"""
        if cls._seg_model is None:
            try:
                # 先尝试从激活的模型中找到分割模型
                from app.services.model_service import ModelService
                model_service = ModelService()
                active_model = model_service.get_active_model()
                
                if active_model and active_model.model_type == "segmentation":
                    seg_model_path = Path(active_model.file_path)
                    if seg_model_path.exists():
                        cls._seg_model = YOLO(str(seg_model_path))
                    else:
                        cls._seg_model = None
                else:
                    # 尝试加载自定义分割模型
                    custom_seg_model = MODEL_DIR / "best-seg.pt"
                    if custom_seg_model.exists():
                        cls._seg_model = YOLO(str(custom_seg_model))
                    else:
                        # 使用预训练的分割模型
                        cls._seg_model = YOLO(YOLO_SEG_MODEL_PATH)
            except Exception as e:
                # 如果出错，使用预训练模型
                cls._seg_model = YOLO(YOLO_SEG_MODEL_PATH)
        
        return cls._seg_model
    
    @classmethod
    def detect(cls, image_path: str) -> DetectionResult:
        """检测图片中的瑕疵"""
        model = cls.get_model()
        image_path_obj = Path(image_path)
        
        if not image_path_obj.exists():
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        
        # 运行检测
        results = model(str(image_path_obj))
        
        # 解析结果
        defects = []
        for result in results:
            boxes = result.boxes
            if boxes is not None and len(boxes) > 0:
                for box in boxes:
                    # 获取边界框坐标
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    
                    # 获取类别名称
                    class_name = model.names.get(class_id, f"class_{class_id}")
                    
                    defects.append(BoundingBox(
                        x1=x1,
                        y1=y1,
                        x2=x2,
                        y2=y2,
                        confidence=confidence,
                        class_name=class_name
                    ))
        
        return DetectionResult(
            image_path=str(image_path),
            defects=defects,
            timestamp=datetime.now()
        )
    
    @classmethod
    def segment(cls, image_path: str, conf_threshold: float = 0.25) -> SegmentResult:
        """分割图片中的瑕疵"""
        model = cls.get_segmentation_model()
        if model is None:
            raise ValueError("分割模型未加载，请确保有可用的分割模型")
        
        image_path_obj = Path(image_path)
        if not image_path_obj.exists():
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        
        # 运行分割
        results = model(str(image_path_obj), conf=conf_threshold)
        
        # 解析结果
        masks = []
        for result in results:
            if result.masks is not None:
                boxes = result.boxes
                seg_masks = result.masks
                
                for idx, mask in enumerate(seg_masks):
                    if boxes is not None and idx < len(boxes):
                        box = boxes[idx]
                        # 获取边界框坐标
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        confidence = float(box.conf[0])
                        class_id = int(box.cls[0])
                        class_name = model.names.get(class_id, f"class_{class_id}")
                    else:
                        # 如果没有box信息，从mask计算
                        mask_data = mask.data[0].cpu().numpy()
                        y_coords, x_coords = np.where(mask_data > 0)
                        if len(x_coords) > 0 and len(y_coords) > 0:
                            x1, x2 = float(x_coords.min()), float(x_coords.max())
                            y1, y2 = float(y_coords.min()), float(y_coords.max())
                        else:
                            continue
                        confidence = 0.5
                        class_id = 0
                        class_name = model.names.get(class_id, "object")
                    
                    # 将mask转换为多边形
                    mask_data = mask.data[0].cpu().numpy().astype(np.uint8) * 255
                    
                    # 使用OpenCV找到轮廓
                    contours, _ = cv2.findContours(mask_data, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    if len(contours) > 0:
                        # 取最大的轮廓
                        largest_contour = max(contours, key=cv2.contourArea)
                        # 简化轮廓（减少点数）
                        epsilon = 0.002 * cv2.arcLength(largest_contour, True)
                        approx = cv2.approxPolyDP(largest_contour, epsilon, True)
                        
                        # 转换为点列表
                        polygon_points = []
                        for point in approx:
                            polygon_points.append(PolygonPoint(
                                x=float(point[0][0]),
                                y=float(point[0][1])
                            ))
                        
                        if len(polygon_points) >= 3:  # 至少3个点才能形成多边形
                            masks.append(SegmentMask(
                                polygon=polygon_points,
                                bbox=BoundingBox(
                                    x1=x1,
                                    y1=y1,
                                    x2=x2,
                                    y2=y2,
                                    confidence=confidence,
                                    class_name=class_name
                                ),
                                confidence=confidence,
                                class_name=class_name
                            ))
        
        return SegmentResult(
            image_path=str(image_path),
            masks=masks,
            timestamp=datetime.now()
        )

