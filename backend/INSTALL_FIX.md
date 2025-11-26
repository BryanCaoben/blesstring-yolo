# Python 3.12 依赖安装修复指南

## 问题说明

Python 3.12 与旧版本的 setuptools/pkg_resources 不兼容，导致构建 numpy 时出错。

## 已修复

✅ 已从 `requirements.txt` 中移除：
- `numpy==1.24.3`
- `opencv-python==4.8.1.78`

这些依赖将由 `ultralytics` 自动安装，避免版本冲突。

## 在服务器上执行以下命令

```bash
# 1. 进入后端目录
cd /home/bryancaoben/ai-platform/BlesstringYolo/backend

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 升级 setuptools 和 wheel（重要！支持 Python 3.12）
pip install --upgrade "setuptools>=68.0" wheel pip

# 4. 卸载可能已安装的有问题的包
pip uninstall numpy opencv-python -y 2>/dev/null || true

# 5. 先安装 ultralytics（它会自动安装兼容的 numpy 和 opencv）
pip install ultralytics==8.3.231

# 6. 安装其他依赖
pip install -r requirements.txt

# 7. 验证安装
python -c "from ultralytics import YOLO; print('✅ ultralytics 导入成功')"
python -c "import numpy; print(f'✅ numpy 版本: {numpy.__version__}')"
python -c "import cv2; print(f'✅ opencv 版本: {cv2.__version__}')"
```

## 如果步骤5失败

如果 `ultralytics` 安装时仍然出错，可以尝试：

```bash
# 使用预编译的 wheel 包（不需要从源码构建）
pip install ultralytics==8.3.231 --only-binary :all:
```

## 验证安装成功

安装完成后，运行以下命令验证：

```bash
python -c "
from ultralytics import YOLO
import numpy as np
import cv2
print('✅ 所有依赖安装成功')
print(f'  - numpy: {np.__version__}')
print(f'  - opencv: {cv2.__version__}')
"
```

## 下一步

安装成功后，可以启动后端服务：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

查看启动日志，确认是否看到：
- ✅ ML后端模块导入成功
- ✅ ML后端路由注册成功: /api/v1/ml/*

