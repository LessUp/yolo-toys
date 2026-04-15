---
date: "2025-11-23"
title: "GPU 与精度相关修改"
---

# 2025-11-23 GPU 与精度相关修改

## 📋 概述

提升默认识别精度，补充多硬件 GPU 使用文档。

## ✨ 新增

- README 新增多硬件 GPU 使用说明（NVIDIA / AMD ROCm / Apple M 系列，本机与 Docker 场景）

## 🔧 变更

- `docker-compose.yml` 中 `MODEL_NAME` 默认值从 `yolov8n.pt` 改为 `yolov8s.pt`，提升默认识别精度
- README 说明默认模型为 `YOLOv8s`，并同步本地运行 / Docker 示例

## 🐛 修复

无

## 📁 文件变更

| 文件 | 操作 |
|------|------|
| `docker-compose.yml` | 修改 |
| `README.md` | 修改 |

---

> 本次更新提升默认模型精度，并完善 GPU 部署文档。
