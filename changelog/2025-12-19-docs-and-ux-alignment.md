---
title: "2025-12-19 — 文档对齐与体验一致性修正"
---

# 2025-12-19 文档对齐与体验一致性修正

- 文档与实现对齐：
  - 更新 `docs/README.md`：同步前端当前函数命名与模块划分（如 `initWS/closeWS`、`updateSidebar`），修正 WebSocket 查询参数列表，完善测试覆盖范围说明，并移除当前接口未返回的字段描述。
  - 更新 `docs/README.md`：在“快速开始/工程工具”补充安装 `requirements-dev.txt`（包含 `pytest` / `pre-commit`）的说明，避免仅安装运行依赖时测试命令失败。

- 前端 UI/UX 细节增强：
  - 更新 `frontend/app.js`：自定义模型输入纳入本地设置持久化，并用于模型类别推断与多模态输入项联动显示。
  - 更新 `frontend/app.js`：避免通用参数变更导致标签页被强制重置，仅在自定义模型输入时同步标签页与模型列表。
  - 更新 `frontend/app.js`：模型卡片支持键盘操作（可聚焦、Enter/Space 触发选择）。
  - 更新 `frontend/app.js`：推理失败时显示后端 `detail`（若存在），并对实时推理错误 toast 做节流，避免刷屏。
  - 更新 `frontend/app.js`：支持按 `Esc` 关闭设置面板。
  - 更新 `frontend/app.js`：启动/切换服务地址时自动请求 `/health`，将 header 版本徽标更新为真实后端版本；后端不可达时展示 `offline` 状态。
  - 更新 `frontend/app.js`：修复启动流程中 `applySettings()` 覆盖当前输入导致的服务地址/模型不一致问题（启动前先保存当前输入并加载模型/健康状态）。
  - 更新 `frontend/app.js`：侧边栏切换逻辑在桌面/移动端互斥处理（`open`/`collapsed`），并在窗口 resize 时自动清理不适用状态，避免显示异常。
  - 更新 `frontend/index.html`：为核心交互按钮与模型选择控件补充 ARIA label，改善可访问性。
  - 更新 `frontend/style.css`：补充 `:focus-visible` 样式提升键盘可访问性；Caption/VQA 面板支持滚动与自动换行；支持 `prefers-reduced-motion` 减少动画。
  - 更新 `frontend/style.css`：侧边栏在桌面端折叠时改为 `width: 0` 平滑收起并释放画布空间；为 `.version-badge` 增加 `offline` 状态样式。
