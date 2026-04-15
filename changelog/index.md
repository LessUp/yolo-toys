---
layout: default
title: "更新日志 — YOLO-Toys"
description: "YOLO-Toys 项目版本历史与变更记录"
---

# 更新日志

YOLO-Toys 项目的版本历史与变更记录，按时间倒序排列。

---

## 版本概览

| 版本 | 发布日期 | 主要变更 |
|------|----------|----------|
| **v3.0** | 2026-02-13 | 架构重构：策略模式、Pydantic Settings、FastAPI lifespan |
| v2.0 | 2025-11-25 | 多模型系统：YOLO/DETR/OWL-ViT/BLIP 支持 |
| v1.x | 2025-02~11 | 基础 YOLO 检测功能、项目基础设施 |

---

## 2026

### 三月

| 日期 | 标题 | 主要变更 |
|------|------|----------|
| [03-10](2026-03-10-pages-round3.md) | GitHub Pages 第三轮优化 | CI paths-ignore、sitemap、404 页面 |
| [03-10](2026-03-10-workflow-deep-standardization.md) | Workflow 深度标准化 | CI/Pages 工作流统一配置 |
| [03-10](2026-03-10-pages-round2.md) | GitHub Pages 第二轮优化 | Changelog 索引、kramdown GFM、SEO 增强 |
| [03-09](2026-03-09-pages-and-docs-optimization.md) | GitHub Pages & 文档优化 | 项目主页重写、SEO 元数据 |

### 二月

| 日期 | 标题 | 主要变更 |
|------|------|----------|
| [02-25](2026-02-25-frontend-ui-beautification.md) | 前端 UI 美化优化 | 字体系统、设计 Token、动效系统 |
| [02-13](2026-02-13-v3-architecture-refactor.md) | **v3.0 架构重构** | 策略模式、Pydantic Settings、测试 6→16 |

---

## 2025

### 十二月

| 日期 | 标题 | 主要变更 |
|------|------|----------|
| [12-19](2025-12-19-docs-and-ux-alignment.md) | 文档对齐与体验修正 | ARIA 可访问性、键盘操作 |
| [12-18](2025-12-18-unify-and-cleanup.md) | 架构统一与前端升级 | 删除遗留文件、API 契约统一 |
| [12-14](2025-12-14-upgrade-and-optimizations.md) | 全面升级与优化 | Grounding DINO、线程池推理、Docker 增强 |

### 十一月

| 日期 | 标题 | 主要变更 |
|------|------|----------|
| [11-25](2025-11-25-multi-model-system.md) | **v2.0 多模型系统** | YOLO/DETR/OWL-ViT/BLIP、Toast 通知 |
| [11-23](2025-11-23-gpu-and-accuracy.md) | GPU 与精度相关修改 | 默认模型升级、多硬件 GPU 文档 |

### 二月

| 日期 | 标题 | 主要变更 |
|------|------|----------|
| [02-13](2025-02-13-project-infrastructure.md) | 项目基础设施优化 | 标准化 badges |

---

## 变更类型说明

| 图标 | 类型 | 说明 |
|:----:|------|------|
| 🚀 | feat | 新功能 |
| 🐛 | fix | Bug 修复 |
| 📚 | docs | 文档变更 |
| 🎨 | style | UI/样式 |
| ♻️ | refactor | 代码重构 |
| ✅ | test | 测试相关 |
| 🔧 | chore | 构建/配置 |

---

## 版本命名规范

遵循 [Semantic Versioning](https://semver.org/)：

- **主版本号 (Major)**: 不兼容的 API 变更
- **次版本号 (Minor)**: 向后兼容的功能新增
- **修订号 (Patch)**: 向后兼容的问题修复

---

[← 返回首页](../)
