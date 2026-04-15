---
date: "2026-03-09"
title: "GitHub Pages & 文档优化"
---

# 2026-03-09 GitHub Pages & 文档优化

## GitHub Pages

1. **重写 `index.md`** — 专业项目主页，包含架构图、模型对比表、特性亮点、技术栈、API 概览、项目结构
2. **优化 `_config.yml`** — 添加 SEO 元数据（url/baseurl/lang）、排除大文件和无关目录（*.pt/app/frontend/tests 等）
3. **优化 `pages.yml` 工作流** — 添加 `paths` 触发条件（仅文档变更触发构建）、`sparse-checkout`（跳过 .pt 大文件）

## 文档同步

4. **修复 `docs/README.md`** — 工程化工具描述从 "Black + Ruff + isort" 更正为 "Ruff lint + format"
5. **更新 `README.md`（英文）** — 添加 CI/Pages 徽章、Grounding DINO 模型、架构图、更完整的目录结构
6. **重写 `README.zh-CN.md`** — 与英文 README 对齐，清理冗余内容（移除 Release 准备等过时段落）、结构化 API/配置表格

## 工程改进

7. **`.gitignore`** — 添加 `.pytest_cache/` 和 `.ruff_cache/`
8. **`.pre-commit-config.yaml`** — pre-commit-hooks v4.6.0 → v5.0.0，ruff v0.6.8 → v0.9.0，新增 `check-added-large-files`
9. **`Makefile`** — 默认 Python 命令 `python3` → `python`（跨平台），新增 `format` target
