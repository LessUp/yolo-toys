---
date: "2026-03-10"
title: "GitHub Pages 第二轮优化"
---

# 2026-03-10 GitHub Pages 第二轮优化

## 📋 概述

文档同步修复，Changelog 可浏览化，Jekyll 配置增强，主页改进。

## ✨ 新增

### Changelog 可浏览化

- 新建 `changelog/index.md` — 更新日志索引页，按年份分组、时间倒序排列
- 所有 changelog `.md` 添加 YAML frontmatter — 使 Jekyll 正式渲染页面

### Jekyll 配置增强

- `_config.yml` 添加 kramdown GFM 设置
- `_config.yml` 添加 `defaults` — 全局默认布局
- `_config.yml` 添加 `jekyll-seo-tag` 插件 — 自动注入 Open Graph / Twitter Card 元数据

### 主页改进

- `index.md` 添加"最近更新"section — 展示最近变更摘要

## 🔧 变更

### 文档同步

- 修复 `docs/README.md` 目录结构 — 与 v3.0 架构对齐
- `pyproject.toml` 描述更正为 "Ruff lint + format"

### Jekyll 配置

- `_config.yml` 扩展 `exclude` — 添加 `Gemfile`、`Gemfile.lock`、`vendor`

### 工作流修复

- `pages.yml` 添加 `sparse-checkout-cone-mode: false` — 修复文件级模式匹配问题

## 🐛 修复

无

## 📁 文件变更

| 文件 | 操作 |
|------|------|
| `docs/README.md` | 修改 |
| `changelog/index.md` | 新增 |
| `changelog/*.md` | 修改 |
| `_config.yml` | 修改 |
| `index.md` | 修改 |
| `.github/workflows/pages.yml` | 修改 |

---

> 本次优化实现 Changelog 可浏览化，增强 Jekyll SEO 配置。
