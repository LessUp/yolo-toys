---
date: "2026-03-09"
title: "GitHub Pages & 文档优化"
---

# 2026-03-09 GitHub Pages & 文档优化

## 📋 概述

GitHub Pages 项目主页重构，文档同步更新，工程化配置优化。

## ✨ 新增

### GitHub Pages

- 重写 `index.md` — 专业项目主页
  - 架构图
  - 模型对比表
  - 特性亮点
  - 技术栈
  - API 概览
  - 项目结构

### 工程改进

- `.gitignore` — 添加 `.pytest_cache/` 和 `.ruff_cache/`
- `.pre-commit-config.yaml` — pre-commit-hooks v4.6.0 → v5.0.0，ruff v0.6.8 → v0.9.0
- Makefile — 新增 `format` target

## 🔧 变更

### GitHub Pages

- 优化 `_config.yml` — 添加 SEO 元数据、排除大文件和无关目录
- 优化 `pages.yml` 工作流 — 添加 `paths` 触发条件、`sparse-checkout`

### 文档同步

- `docs/README.md` — 工程化工具描述更正为 "Ruff lint + format"
- `README.md` — 添加 CI/Pages 徽章、Grounding DINO 模型、架构图
- `README.zh-CN.md` — 与英文 README 对齐，清理冗余内容

### 工程改进

- Makefile — 默认 Python 命令 `python3` → `python`（跨平台）

## 🐛 修复

无

## 📁 文件变更

| 文件 | 操作 |
|------|------|
| `index.md` | 重写 |
| `_config.yml` | 修改 |
| `.github/workflows/pages.yml` | 修改 |
| `docs/README.md` | 修改 |
| `README.md` | 修改 |
| `README.zh-CN.md` | 重写 |
| `.gitignore` | 修改 |
| `.pre-commit-config.yaml` | 修改 |
| `Makefile` | 修改 |

---

> 本次更新重构项目主页，优化文档结构和工程配置。
