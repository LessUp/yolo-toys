---
date: "2025-12-18"
title: "架构统一与前端升级"
---

# 2025-12-18 架构统一与前端升级

## 📋 概述

删除历史遗留文件，统一 API 返回结构，增强前端交互一致性，补齐测试覆盖。

## ✨ 新增

### 测试覆盖

- `/infer`、`/caption`、`/vqa` 的基础 smoke tests
- 通过 `monkeypatch` mock `model_manager.infer`，避免测试依赖真实模型下载/推理

## 🔧 变更

### 清理遗留文件

删除历史遗留文件，避免新旧实现并存造成维护负担：

- `app/main_old.py`
- `app/inference.py`
- `frontend/index_old.html`
- `frontend/style_old.css`
- `frontend/app_old.js`

### API 契约统一

- `app/schemas.py`：`InferenceResponse.task` 扩展支持 `caption`/`vqa`
- `app/main.py`：为 `/infer`、`/caption`、`/vqa` 增加 `response_model=InferenceResponse`
- `app/main.py`：抽取 `_read_upload_image` 统一图片读取/解码与大小限制校验
- `app/main.py`：`ValueError` 映射为 HTTP 400（不再返回 500）

### 前端交互增强

- 构建模型 ID 到类别的索引，选择模型时自动同步标签页
- 根据当前模型类别动态显示/隐藏"开放词汇查询 / VQA 问题"输入
- 图片上传推理复用 `handleResult`，展示 Caption/VQA 输出

### 测试命令可移植性

- `make test` 改为执行 `python -m pytest`
- CI、CONTRIBUTING、README 同步测试命令

## 🐛 修复

无

## 📁 文件变更

| 文件 | 操作 |
|------|------|
| `app/main.py` | 修改 |
| `app/schemas.py` | 修改 |
| `app/main_old.py` | 删除 |
| `app/inference.py` | 删除 |
| `frontend/index_old.html` | 删除 |
| `frontend/style_old.css` | 删除 |
| `frontend/app_old.js` | 删除 |
| `frontend/index.html` | 修改 |
| `frontend/app.js` | 修改 |
| `tests/test_api.py` | 修改 |
| `Makefile` | 修改 |
| `docs/README.md` | 修改 |
| `README.md` | 修改 |
| `CONTRIBUTING.md` | 修改 |
| `.github/workflows/ci.yml` | 修改 |

---

> 本次更新清理历史遗留代码，统一 API 契约，提升代码质量和测试覆盖。
