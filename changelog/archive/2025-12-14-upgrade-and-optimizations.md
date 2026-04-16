---
date: "2025-12-14"
title: "全面升级与优化"
---

# 2025-12-14 全面升级与优化

## 📋 概述

修复测试用例，优化后端配置与稳定性，补齐多模型能力，增强前端交互和部署体验。

## ✨ 新增

### 后端配置优化

- 从环境变量读取默认推理参数：`CONF_THRESHOLD`、`IOU_THRESHOLD`、`MAX_DET`
- `/health` 返回体补充 `defaults` 字段，便于前端/运维查看当前默认参数

### 多模型能力补齐

- `ModelManager` 新增 Grounding DINO 的加载与推理实现

### 前端交互完善

- 将多模态参数（`text_queries`、`question`）纳入本地设置持久化
- HTTP `/infer` 与 WebSocket `/ws` 请求同步携带完整参数
- 支持在 WebSocket 运行时发送 `config` 消息动态更新模型与推理参数
- 在界面统一展示 Caption 与 VQA 结果

### 易部署增强

- Dockerfile：支持 `PORT` 环境变量启动
- Dockerfile：将仓库内 `yolov8*.pt` 权重复制进镜像，减少首次联网依赖
- docker-compose：增加 `restart: unless-stopped`、`healthcheck` 与缓存卷
- `.env.example`：补齐 `PORT`、`ALLOW_ORIGINS`、`MAX_UPLOAD_MB`、`MAX_CONCURRENCY` 等常用部署配置
- Makefile：`docker-run` 默认使用 `ENV_FILE?=.env.example`

## 🔧 变更

- `/infer`、`/caption`、`/vqa` 将推理调用移入线程池（`asyncio.to_thread`），避免阻塞事件循环
- `/caption`、`/vqa` 返回体补充 `model` 字段，保持与 `/infer` 行为一致
- 清理 `model_manager.py` 中未使用导入

## 🐛 修复

- 修复测试用例与新版 API 返回结构不一致的问题

## 📁 文件变更

| 文件 | 操作 |
|------|------|
| `app/model_manager.py` | 修改 |
| `app/main.py` | 修改 |
| `frontend/app.js` | 修改 |
| `Dockerfile` | 修改 |
| `docker-compose.yml` | 修改 |
| `.env.example` | 修改 |
| `Makefile` | 修改 |
| `README.md` | 修改 |
| `tests/test_api.py` | 修改 |

---

> 本次更新修复测试问题，优化配置管理和部署体验，新增 Grounding DINO 支持。
