---
date: "2026-03-10"
title: "Workflow 深度标准化"
---

# 2026-03-10 Workflow 深度标准化

## 📋 概述

全仓库 GitHub Actions 深度标准化：统一命名、权限、并发、路径过滤与缓存策略。

## ✨ 新增

无

## 🔧 变更

### CI Workflow

- 统一 `permissions: contents: read`
- 统一 `concurrency` 配置

### Pages Workflow

- 补充 `actions/configure-pages@v5` 步骤
- 添加 `paths` 触发过滤，减少无效构建

## 🐛 修复

无

## 📁 文件变更

| 文件 | 操作 |
|------|------|
| `.github/workflows/ci.yml` | 修改 |
| `.github/workflows/pages.yml` | 修改 |

---

> 本次标准化统一 GitHub Actions 配置规范，提升 CI/CD 效率。
