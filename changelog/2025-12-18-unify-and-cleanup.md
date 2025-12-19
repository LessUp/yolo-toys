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
