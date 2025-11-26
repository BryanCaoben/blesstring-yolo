# LabelStudio ML后端配置指南

本指南说明如何在LabelStudio中配置ML后端，启用自动分割预标注功能。

## 功能说明

配置ML后端后，LabelStudio可以：
- **自动预标注**：上传图片时自动运行YOLOv8-seg分割模型
- **实时预测**：在标注过程中提供智能建议
- **提升效率**：大幅减少手动标注时间

## 配置步骤

### 1. 确认后端服务运行

确保FastAPI后端服务正在运行：

```bash
# 检查服务是否运行
curl http://localhost:8000/api/v1/ml/health

# 应该返回: {"status": "UP"}
```

### 2. 在LabelStudio中配置ML后端

#### 方式一：通过Web界面配置（推荐）

1. **登录LabelStudio**
   - 访问 LabelStudio 地址（通常是 `http://localhost:8080`）

2. **进入项目设置**
   - 选择或创建要配置的项目
   - 点击项目设置（Settings）

3. **添加ML后端**
   - 在设置页面找到 "Machine Learning" 或 "ML Backend" 部分
   - 点击 "Add ML Backend" 或 "Connect Model"

4. **填写ML后端URL**
   ```
   http://your-server-ip:8000/api/v1/ml
   ```
   
   > 注意：将 `your-server-ip` 替换为你的实际服务器IP地址
   > 
   > 示例：
   > - 本地开发：`http://localhost:8000/api/v1/ml`
   > - 远程服务器：`http://192.168.1.100:8000/api/v1/ml`

5. **保存配置**
   - 点击 "Save" 或 "Connect"
   - 如果配置成功，会显示 "Connected" 状态

#### 方式二：通过API配置

```bash
# 获取LabelStudio API Token（在用户设置中）
export LABEL_STUDIO_TOKEN="your_token_here"
export PROJECT_ID=1
export ML_BACKEND_URL="http://your-server-ip:8000/api/v1/ml"

# 创建ML后端连接
curl -X POST "http://localhost:8080/api/ml-backends/" \
  -H "Authorization: Token $LABEL_STUDIO_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"YOLOv8 Segmentation Backend\",
    \"url\": \"$ML_BACKEND_URL\"
  }"

# 将ML后端连接到项目
curl -X POST "http://localhost:8080/api/projects/$PROJECT_ID/ml-backends/" \
  -H "Authorization: Token $LABEL_STUDIO_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"ml_backend\": <backend_id>
  }"
```

### 3. 启用自动预标注

在项目设置中：
1. 找到 "Predictions" 或 "自动预标注" 选项
2. 启用 "Enable auto-annotation" 或 "自动标注"
3. 保存设置

### 4. 测试配置

1. **上传测试图片**
   - 在LabelStudio项目中导入一张图片

2. **检查预标注结果**
   - 图片上传后，应该自动出现分割标注
   - 标注格式为多边形（polygon）

3. **查看标注界面**
   - 打开图片进行标注
   - 应该可以看到预标注的多边形区域

## 模型配置

### 使用预训练模型

系统默认使用YOLOv8n-seg预训练模型（首次使用会自动下载）。

### 使用自定义分割模型

1. **上传分割模型**
   - 在"模型管理"页面上传训练好的`.pt`分割模型
   - 选择模型类型为"分割模型"

2. **激活分割模型**
   - 在模型列表中点击"激活"
   - 系统会自动使用激活的分割模型

3. **模型文件命名**
   - 可以上传命名为 `best-seg.pt` 的分割模型到 `models/` 目录
   - 系统会优先使用此模型

## 故障排查

### ML后端连接失败

**问题**：LabelStudio显示无法连接到ML后端

**解决方案**：
1. 检查后端服务是否运行：`curl http://localhost:8000/api/v1/ml/health`
2. 检查防火墙设置，确保8000端口开放
3. 检查URL是否正确（包含 `/api/v1/ml`）
4. 检查CORS设置（后端已配置允许所有来源）

### 没有自动预标注

**问题**：上传图片后没有自动标注

**解决方案**：
1. 确认ML后端已正确连接（状态为"Connected"）
2. 检查项目设置中的"自动预标注"是否已启用
3. 查看后端日志，确认是否有预测请求
4. 检查分割模型是否已加载

### 分割结果不准确

**问题**：预标注的分割结果不准确

**解决方案**：
1. 使用自定义训练的分割模型（针对乐器瑕疵优化）
2. 调整模型置信度阈值（在代码中修改 `conf_threshold`）
3. 手动修正预标注结果（这是正常的，预标注只是辅助）

## API端点说明

ML后端提供以下端点：

- `GET /api/v1/ml/health` - 健康检查
- `POST /api/v1/ml/predict` - 预测接口（LabelStudio自动调用）
- `POST /api/v1/ml/setup` - 设置接口

## 工作流程

```
用户上传图片到LabelStudio
    ↓
LabelStudio调用ML后端 /predict 接口
    ↓
后端加载YOLOv8-seg模型
    ↓
执行分割预测
    ↓
转换为LabelStudio格式（polygon）
    ↓
返回预标注结果
    ↓
LabelStudio自动填充到标注界面
    ↓
用户检查和微调标注
```

## 注意事项

1. **首次使用**：YOLOv8-seg模型首次下载可能需要一些时间
2. **性能**：分割预测比检测慢，大图片可能需要几秒钟
3. **GPU加速**：如果有GPU，建议在配置中设置 `device="cuda"` 以提升速度
4. **模型切换**：切换模型后，需要重启后端服务或清除模型缓存

## 相关文件

- ML后端API实现：`backend/app/api/ml_backend.py`
- 分割服务：`backend/app/services/yolo_service.py` (segment方法)
- 模型管理：`backend/app/services/model_service.py`

---

配置完成后，你就可以享受自动分割预标注带来的效率提升了！🚀

