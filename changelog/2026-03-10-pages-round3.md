---
date: "2026-03-10"
title: "GitHub Pages 第三轮优化"
---

# 2026-03-10 GitHub Pages 第三轮优化

## 📋 概述

CI/Pages 工作流优化，Jekyll 配置增强，新增自定义 404 页面。

## ✨ 新增

### Jekyll 配置增强

- 添加 `jekyll-sitemap` 插件 — 自动生成 `sitemap.xml`

### 新增文件

- `404.md` — 自定义 404 错误页面，提供返回首页链接

## 🔧 变更

### CI 工作流优化

- `ci.yml` 添加 `paths-ignore` — 文档变更不再触发 CI 构建
- 移除冗余 `master` 分支触发条件

### Pages 工作流优化

- `cancel-in-progress` 改为 `true` — 自动取消旧的构建任务
- `sparse-checkout` 添加 `404.md`

### 文档修正

- `docs/README.md` — `python3` 改为 `python`（跨平台兼容）
- `index.md` — 添加 Pages 部署状态 badge

## 🐛 修复

无

## 📁 文件变更

| 文件 | 操作 |
|------|------|
| `.github/workflows/ci.yml` | 修改 |
| `.github/workflows/pages.yml` | 修改 |
| `_config.yml` | 修改 |
| `404.md` | 新增 |
| `docs/README.md` | 修改 |
| `index.md` | 修改 |
| `changelog/index.md` | 修改 |

---

> 本次优化节省 CI 分钟数，改善搜索引擎索引，提升用户体验。
