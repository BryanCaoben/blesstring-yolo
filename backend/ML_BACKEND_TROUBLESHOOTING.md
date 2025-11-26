# ML后端路由问题排查指南

## 问题：`/api/v1/ml/health` 返回 404 Not Found

### 排查步骤

#### 1. 检查后端服务启动日志

重启后端服务，查看是否有错误信息：

```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

查看输出中是否有：
- ✅ `ML后端模块导入成功`
- ✅ `ML后端路由注册成功: /api/v1/ml/*`
- 或者 ❌ `警告: ML后端模块导入失败`
- 或者 ❌ `警告: ML后端路由未注册`

#### 2. 测试模块导入

运行测试脚本：

```bash
cd backend
source venv/bin/activate
python test_ml_backend_import.py
```

应该看到：
- ✅ ml_backend模块导入成功
- ✅ router对象信息
- ✅ 路由列表（health, predict, setup）

#### 3. 检查文件是否存在

```bash
ls -la backend/app/api/ml_backend.py
```

#### 4. 手动测试导入

```bash
cd backend
source venv/bin/activate
python -c "from app.api import ml_backend; print(ml_backend.router)"
```

#### 5. 检查API文档

访问：http://localhost:8000/docs

在Swagger UI中查找：
- 是否有 "LabelStudio ML Backend" 标签页
- 是否有 `/api/v1/ml/health` 端点

#### 6. 直接测试路由

```bash
# 测试health端点
curl http://localhost:8000/api/v1/ml/health

# 应该返回: {"status":"UP"}
```

### 常见问题

#### 问题1：模块导入失败

**现象**：启动日志显示"ML后端模块导入失败"

**可能原因**：
- 文件语法错误
- 导入依赖缺失
- 循环导入

**解决方法**：
1. 检查Python语法：`python -m py_compile backend/app/api/ml_backend.py`
2. 检查依赖是否安装：`pip list | grep aiofiles`
3. 查看详细错误信息（已在main.py中添加）

#### 问题2：路由未注册

**现象**：模块导入成功，但路由未注册

**可能原因**：
- router对象为空
- 路由注册代码未执行

**解决方法**：
1. 检查ml_backend.py中router是否正确定义
2. 检查main.py中路由注册代码是否执行

#### 问题3：路由注册但404

**现象**：路由已注册，但访问404

**可能原因**：
- 路径前缀错误
- 路由冲突

**解决方法**：
1. 检查main.py中的prefix：`prefix="/api/v1/ml"`
2. 检查完整路径应该是：`/api/v1/ml/health`

### 快速修复

如果问题仍然存在，尝试以下操作：

1. **清理Python缓存**：
```bash
find backend -type d -name __pycache__ -exec rm -r {} +
find backend -type f -name "*.pyc" -delete
```

2. **重新导入模块**：
```bash
cd backend
python -c "import sys; sys.path.insert(0, '.'); from app.api import ml_backend; print('OK')"
```

3. **检查路由列表**：
访问 http://localhost:8000/openapi.json，搜索 "ml" 或 "/api/v1/ml"

### 如果仍然无法解决

请提供以下信息：
1. 后端服务启动时的完整日志
2. 运行 `python test_ml_backend_import.py` 的输出
3. 访问 http://localhost:8000/docs 的截图
4. 运行 `curl -v http://localhost:8000/api/v1/ml/health` 的输出

