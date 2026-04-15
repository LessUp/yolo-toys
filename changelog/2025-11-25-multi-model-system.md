---
date: "2025-11-25"
title: "多模型系统增强"
---

# 2025-11-25 多模型系统增强

## 📋 概述

全面增强项目，支持多种 AI 模型的动态切换，包括 YOLO 系列、HuggingFace Transformers 模型和多模态模型。同时深度优化前端界面的设计和交互体验。版本升级至 **v2.0.0**。

## ✨ 新增

### 多模型支持系统

| 类型 | 模型 | 说明 |
|------|------|------|
| YOLO 检测 | YOLOv8n/s/m/l/x | 目标检测模型 |
| YOLO 分割 | YOLOv8n/s/m-seg | 实例分割模型 |
| YOLO 姿态 | YOLOv8n/s/m-pose | 人体姿态估计模型 |
| Transformer | DETR ResNet-50/101 | 端到端目标检测 |
| 开放词汇 | OWL-ViT | 支持任意文本描述检测 |
| 多模态 | BLIP Caption | 图像自动描述生成 |
| 多模态 | BLIP VQA | 视觉问答 |

### 新增后端文件

- `app/model_manager.py` — 统一模型管理器
  - 支持多种模型类别和动态切换
  - 模型缓存和自动设备选择
  - 统一推理接口

### API 增强

- `GET /models` — 返回所有可用模型，按类别分组
- `GET /models/{model_id}` — 获取指定模型详细信息
- `POST /infer` — 增加 `text_queries` 和 `question` 参数
- `POST /caption` — 新增图像描述生成端点
- `POST /vqa` — 新增视觉问答端点
- WebSocket 支持运行时配置更新

### 前端 UI 全新设计

- 现代化深色/浅色主题设计
- 模型类别标签页快速切换
- 顶部快速模型选择下拉框
- 实时性能叠加层显示
- 图像描述结果展示区域
- Toast 通知系统
- 错误处理增强

## 🔧 变更

- 为所有设置项添加悬浮提示 (Tooltips)
- 修复模型标签页过滤逻辑
- 添加模型卡片的速度/精度元信息显示
- 修复 WebSocket 断开重连时的通知显示

## 🐛 修复

- 摄像头权限、网络错误等友好提示

## 📦 依赖更新

```
transformers>=4.35.0  # HuggingFace Transformers
accelerate>=0.24.0    # 推理加速
```

## 📁 文件变更

| 文件 | 操作 |
|------|------|
| `app/model_manager.py` | 新增 |
| `app/main.py` | 修改 |
| `frontend/index.html` | 修改 |
| `frontend/style.css` | 修改 |
| `frontend/app.js` | 修改 |
| `requirements.txt` | 修改 |
| `changelog/2025-11-25-multi-model-system.md` | 新增 |

## 💡 使用说明

### 切换模型

1. 在设置面板中选择模型类别标签页
2. 点击模型卡片选择具体模型
3. 或使用顶部快速选择下拉框

### 多模态功能

1. 选择"多模态"类别
2. 图像描述：选择 BLIP Caption 模型，自动生成描述
3. 视觉问答：选择 BLIP VQA 模型，在设置中输入问题

### 开放词汇检测

1. 选择 OWL-ViT 模型
2. 在多模态设置中输入要检测的物体（逗号分隔）
3. 例如: `person, red car, dog`

## ⚠️ 注意事项

- HuggingFace 模型首次使用需要下载，请确保网络连接
- 多模态模型需要更多内存，建议使用 GPU
- 原有的 YOLO 功能完全兼容

---

> 本次为重大功能更新，引入多模型支持系统，版本升级至 v2.0.0。
