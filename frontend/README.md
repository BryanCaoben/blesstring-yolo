# 前端项目说明

## 技术栈

- **React 18** - UI框架
- **Ant Design 5** - UI组件库
- **Vite** - 构建工具
- **Axios** - HTTP客户端

## 项目结构

```
frontend/
├── src/
│   ├── App.jsx                    # 主应用组件
│   ├── main.jsx                   # 应用入口
│   ├── index.css                  # 全局样式
│   ├── components/                # React组件
│   │   ├── ImageUpload/          # 图片上传组件
│   │   └── DetectionResult/      # 检测结果展示组件
│   └── services/
│       └── api.js                # API调用服务
├── index.html                     # HTML模板
├── vite.config.js                # Vite配置
└── package.json                  # 依赖配置
```

## 启动开发服务器

```bash
npm install    # 首次运行安装依赖
npm run dev    # 启动开发服务器
```

访问 http://localhost:3000

## 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录

## 主要组件

### ImageUpload
- 支持拖拽上传
- 文件类型验证
- 上传进度显示

### DetectionResult
- 检测结果可视化
- Canvas绘制检测框
- 置信度显示

## API代理配置

开发模式下，Vite会自动代理 `/api` 请求到后端服务器（`http://localhost:8000`）

配置在 `vite.config.js` 中：

```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true
  }
}
```

## 生产环境部署

1. 修改API地址：更新 `src/services/api.js` 中的 `API_BASE_URL`
2. 构建项目：`npm run build`
3. 部署 `dist/` 目录到Web服务器（如Nginx）

