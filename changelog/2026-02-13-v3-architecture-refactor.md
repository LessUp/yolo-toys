---
title: "v3.0.0 — 架构重构 (2026-02-13)"
---

# v3.0.0 - 架构重构 (2026-02-13)

## 概述
对整个项目进行彻底重构优化，提升代码可维护性、可扩展性和测试覆盖率。

## 后端重构

### 策略模式拆分 model_manager.py (814 行 → ~100 行)
- 新增 `app/handlers/` 模块，包含：
  - `base.py` - `BaseHandler` 抽象基类，定义统一的 `load()` / `infer()` 接口
  - `registry.py` - `HandlerRegistry` 处理器工厂 + `MODEL_REGISTRY` 模型元数据
  - `yolo_handler.py` - YOLO 检测/分割/姿态处理器
  - `hf_handler.py` - DETR / OWL-ViT / Grounding DINO 处理器
  - `blip_handler.py` - BLIP Caption / VQA 处理器
- `model_manager.py` 简化为纯委托层，通过 `HandlerRegistry` 自动路由

### Pydantic Settings 统一配置
- 新增 `app/config.py`，使用 `pydantic-settings` 管理所有环境变量
- 替代 `main.py` 中散乱的 `os.getenv()` 调用
- 支持 `.env` 文件自动加载、类型校验、属性派生（`origins_list`、`max_upload_bytes`）

### FastAPI 现代化
- `main.py` 使用 `lifespan` 上下文管理器替代已弃用的 `@app.on_event("startup")`
- 路由提取到 `app/routes.py`，`main.py` 仅保留应用初始化和中间件配置
- 全局 `print()` 替换为 `logging` 结构化日志

## 前端优化
- 提取 `buildInferUrl()` / `buildWsUrl()` 公共函数
- 消除 `sendFrame`、`runImageInference`、`initWS` 中的 URL 构建重复代码
- 更新设置存储 key 版本

## 基础设施
- `docker-compose.yml` 移除已废弃的 `version` 字段
- `.gitignore` 增强：添加 `.env`、IDE 配置、模型权重（`*.pt`）等
- `.dockerignore` 增强：排除 tests/docs/changelog 等非运行时文件
- `pyproject.toml` 完善：添加 `[project]` 元数据，ruff 升级到 `[tool.ruff.lint]` 格式
- `requirements.txt` 添加 `pydantic-settings>=2.1.0`

## 测试增强
- 新增 WebSocket 连接/推理/配置更新测试
- 新增 model info 端点（404/200）测试
- 新增边界输入测试（无效 content-type、空文件、缺少必填参数）
- 新增 `HandlerRegistry` 单元测试
- 新增 `AppSettings` 配置测试
- 测试用例从 6 个增加到 16 个

## 文件变更统计
- 新增文件：`app/config.py`、`app/routes.py`、`app/handlers/{__init__,base,registry,yolo_handler,hf_handler,blip_handler}.py`
- 重写文件：`app/main.py`（410→91 行）、`app/model_manager.py`（814→105 行）
- 更新文件：`tests/test_api.py`、`requirements.txt`、`pyproject.toml`、`.gitignore`、`.dockerignore`、`docker-compose.yml`、`README.md`
