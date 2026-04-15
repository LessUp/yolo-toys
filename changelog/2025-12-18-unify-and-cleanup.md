---
date: "2025-12-18"
title: "架构统一与前端升级"
---

# 2025-12-18 架构统一与前端升级

- 删除历史遗留文件，避免新旧实现并存造成维护负担：
  - `app/main_old.py`
  - `frontend/index_old.html`
  - `frontend/style_old.css`
  - `frontend/app_old.js`

- 删除旧版推理模块，避免与多模型管理器重复：
  - `app/inference.py`

- 同步统一 API 返回结构与文档描述：
  - 更新 `app/schemas.py`：`InferenceResponse.task` 扩展支持 `caption`/`vqa`，并补充 `caption`/`question`/`answer`/`text_queries` 字段。
  - 更新 `docs/README.md` 与根 `README.md`：移除 `app/inference.py` 引用，明确 `app/model_manager.py` 为统一推理核心。
  - 更新 `docs/README.md`：技术栈/关键依赖补充 `torch`、`transformers`、`accelerate` 等多模型运行依赖。

- 前端多模型与多模态体验补齐：
  - 更新 `frontend/index.html`：模型标签页新增 `hf_owlvit` 与 `hf_grounding_dino`，并扩展开放词汇查询提示文案。
  - 更新 `frontend/app.js`：图片上传推理复用 `handleResult`，在图片模式也能展示 Caption/VQA 输出，并优化状态栏摘要显示。

- 补齐核心接口测试覆盖：
  - 更新 `tests/test_api.py`：新增 `/infer`、`/caption`、`/vqa` 的基础 smoke tests，并通过 `monkeypatch` mock `model_manager.infer`，避免测试依赖真实模型下载/推理。

- 后端契约与一致性增强：
  - 更新 `app/main.py`：为 `/infer`、`/caption`、`/vqa` 增加 `response_model=InferenceResponse`（并启用 `response_model_exclude_none`），统一返回结构约束。
  - 更新 `app/main.py`：抽取 `_read_upload_image` 统一图片读取/解码与 `MAX_UPLOAD_MB` 大小限制校验，补齐 `/caption`、`/vqa` 与 `/infer` 的行为一致性。
  - 更新 `app/main.py`：启动预热推理调用统一为关键字参数传递；并将模型/参数类 `ValueError` 映射为 HTTP 400（不再返回 500），提升 API 契约语义一致性。

- 测试命令可移植性优化：
  - 更新 `Makefile`：`make test` 改为执行 `python -m pytest`，避免环境缺少 `pytest` 可执行文件导致失败。
  - 更新 `README.md`：测试示例命令同步改为 `python -m pytest`。
  - 更新 `docs/README.md`：`make test` 说明同步为执行 `python -m pytest`。
  - 更新 `.github/workflows/ci.yml` 与 `CONTRIBUTING.md`：测试命令同步为 `python -m pytest`。

- 前端交互一致性增强：
  - 更新 `frontend/app.js`：构建 `model_id -> category` 索引；选择模型时自动同步标签页；并根据当前模型类别动态显示/隐藏"开放词汇查询 / VQA 问题"输入，减少无关配置干扰。
