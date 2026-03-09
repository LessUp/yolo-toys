---
title: "2026-03-10 — GitHub Pages 第二轮优化"
---

# 2026-03-10 — GitHub Pages 第二轮优化

## 文档同步

1. **修复 `docs/README.md` 目录结构** — 第 4 节目录树与 v3.0 架构对齐（添加 `config.py`、`routes.py`、`handlers/`、`js/` 模块），`pyproject.toml` 描述从 "Black / Ruff / isort" 更正为 "Ruff lint + format"

## Changelog 可浏览化

2. **新建 `changelog/index.md`** — 更新日志索引页，按年份分组、时间倒序排列，可在 GitHub Pages 上直接浏览
3. **所有 changelog `.md` 添加 YAML frontmatter** — 9 个文件添加 `title` 字段，使 Jekyll 将其渲染为正式页面（而非原始 Markdown 文件）

## Jekyll 配置增强

4. **`_config.yml` 添加 kramdown GFM 设置** — 明确指定 `markdown: kramdown` + `input: GFM` + `syntax_highlighter: rouge`，改善表格和代码块渲染
5. **`_config.yml` 添加 `defaults`** — 全局默认 `layout: default`，changelog 目录也默认使用 default 布局，无需每个文件重复指定
6. **`_config.yml` 添加 `jekyll-seo-tag` 插件** — 自动注入 Open Graph / Twitter Card 元数据，改善社交分享预览
7. **`_config.yml` 扩展 `exclude`** — 添加 `Gemfile`、`Gemfile.lock`、`vendor` 排除项

## 主页改进

8. **`index.md` 添加"最近更新"section** — 在 API 概览之后、文档链接之前展示最近 4 条变更摘要 + "查看完整更新日志"链接

## 工作流修复

9. **`pages.yml` 添加 `sparse-checkout-cone-mode: false`** — 修复 sparse checkout 默认 cone 模式不支持文件级模式匹配的问题，确保 `index.md`、`_config.yml` 等顶层文件被正确检出
