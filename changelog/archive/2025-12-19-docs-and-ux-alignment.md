---
date: "2025-12-19"
title: "文档对齐与体验一致性修正"
---

# 2025-12-19 文档对齐与体验一致性修正

## 📋 概述

文档与实现对齐，前端 UI/UX 细节增强，提升可访问性和用户体验。

## ✨ 新增

### 前端增强

- 自定义模型输入纳入本地设置持久化
- 模型卡片支持键盘操作（可聚焦、Enter/Space 触发选择）
- 支持按 `Esc` 关闭设置面板
- 启动/切换服务地址时自动请求 `/health`，header 版本徽标更新为真实后端版本
- 后端不可达时展示 `offline` 状态
- 推理失败时显示后端 `detail`（若存在）
- 实时推理错误 toast 节流，避免刷屏

### 可访问性增强

- 为核心交互按钮与模型选择控件补充 ARIA label
- 补充 `:focus-visible` 样式提升键盘可访问性
- 支持 `prefers-reduced-motion` 减少动画

## 🔧 变更

### 文档同步

- `docs/README.md`：同步前端当前函数命名与模块划分
- `docs/README.md`：修正 WebSocket 查询参数列表
- `docs/README.md`：补充安装 `requirements-dev.txt` 说明

### 前端优化

- 避免通用参数变更导致标签页被强制重置
- 侧边栏切换逻辑在桌面/移动端互斥处理
- 窗口 resize 时自动清理不适用状态
- Caption/VQA 面板支持滚动与自动换行
- 侧边栏在桌面端折叠时平滑收起并释放画布空间

## 🐛 修复

- 修复启动流程中 `applySettings()` 覆盖当前输入导致的服务地址/模型不一致问题

## 📁 文件变更

| 文件 | 操作 |
|------|------|
| `docs/README.md` | 修改 |
| `frontend/index.html` | 修改 |
| `frontend/app.js` | 修改 |
| `frontend/style.css` | 修改 |

---

> 本次更新完善文档一致性，提升前端可访问性和用户体验。
