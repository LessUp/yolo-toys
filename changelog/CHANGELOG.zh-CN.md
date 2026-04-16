# 更新日志

本项目的所有显著变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/spec/v2.0.0.html)。

---

## [未发布]

### 新增
- 预留即将发布的功能

---

## [3.1.0] - 2026-04-16

### 📝 文档系统重构

本次发布专注于全面的文档改进和双语支持。

### 新增
- 专业化双语文档系统（英文/中文）
- 重构 `docs/` 目录，分类组织：
  - `getting-started/` — 安装和快速入门指南
  - `api/` — REST API 和 WebSocket 协议文档
  - `architecture/` — 系统设计和处理器模式文档
  - `deployment/` — Docker 和生产部署指南
  - `guides/` — 开发教程（添加自定义模型）
  - `reference/` — 快速参考资料（模型、FAQ）
- 遵循 Keep a Changelog 格式的标准化更新日志
- 完整的 API 参考，包含请求/响应示例
- 解释设计模式的架构文档（策略、注册表、模板方法）
- 带性能基准的模型兼容性矩阵
- 涵盖安装、性能和故障排除的综合 FAQ

### 变更
- 文档导航优化，分类清晰
- 英文和中文文档之间的交叉链接
- 所有文档中的增强代码示例

### 文档
- 所有文档现提供中英文双语版本
- README.md 和 README.zh-CN.md 相互引用
- 更新日志遵循 Keep a Changelog 规范

---

## [3.0.0] - 2026-02-13

### 🏗️ 架构重构

采用策略模式实现的重大架构改进，提升可维护性。

### 新增
- **策略模式架构**：新增 `app/handlers/` 模块
  - `base.py` — BaseHandler 抽象类，统一接口
  - `registry.py` — HandlerRegistry 工厂和 MODEL_REGISTRY 元数据
  - `yolo_handler.py` — YOLO 检测/分割/姿态处理器
  - `hf_handler.py` — DETR / OWL-ViT / Grounding DINO 处理器
  - `blip_handler.py` — BLIP 描述 / VQA 处理器
- **Pydantic 设置**：`app/config.py` 中统一的环境配置
  - 类型验证和 `.env` 文件支持
  - 计算设置的派生属性
- **增强测试**：测试用例从 6 个增加到 16+ 个
  - WebSocket 连接/推理/配置更新测试
  - 模型信息端点测试（404/200）
  - 边界输入测试（无效 content-type、空文件）
  - HandlerRegistry 单元测试
  - AppSettings 配置测试
- **现代 FastAPI 模式**
  - Lifespan 上下文管理器替代已弃用的 `@app.on_event`
  - 路由提取到专门的 `routes.py`
  - 结构化日志替代 print 语句

### 变更
- `model_manager.py` 从 814 行简化为约 100 行
- `main.py` 从 410 行精简到 91 行
- 前端 URL 构建提取为公共函数
- 增强 `.gitignore` 和 `.dockerignore`
- `pyproject.toml` 更新 `[project]` 元数据

### 移除
- 弃用的 `on_event("startup")` 用法
- Model Manager 中的冗余代码

---

## [2.0.0] - 2025-11-25

### 🎯 多模型系统

全面支持多 AI 模型动态切换。

### 新增
- **多模型支持系统**
  - YOLO 检测：YOLOv8 n/s/m/l/x
  - YOLO 分割：YOLOv8-seg 系列
  - YOLO 姿态：YOLOv8-pose 系列
  - Transformer：DETR ResNet-50/101
  - 开放词汇：OWL-ViT 零样本检测
  - 多模态：BLIP 描述和视觉问答
- **新 API 端点**
  - `GET /models` — 按类别列出所有可用模型
  - `GET /models/{model_id}` — 获取模型详情
  - `POST /caption` — 图像描述
  - `POST /vqa` — 视觉问答
  - 运行时 WebSocket 配置更新
- **前端 UI 全面改版**
  - 现代深色/浅色主题设计
  - 模型类别标签页快速切换
  - Toast 通知系统
  - 实时性能叠加显示
  - localStorage 设置持久化

### 变更
- 通过 ModelManager 统一模型管理
- 标准化 API 响应格式
- 使用 ES Modules 重构前端

---

## [1.0.0] - 2025-02-13

### 🚀 项目启动

初始项目基础设施和基础 YOLO 功能。

### 新增
- FastAPI 后端，支持 REST 端点
- YOLOv8 目标检测支持
- WebSocket 流式实时检测
- 基础 HTML/CSS/JS 前端
- Docker 支持
- GitHub Actions CI/CD

---

## 发布链接格式

- [3.1.0]: https://github.com/LessUp/yolo-toys/releases/tag/v3.1.0
- [3.0.0]: https://github.com/LessUp/yolo-toys/releases/tag/v3.0.0
- [2.0.0]: https://github.com/LessUp/yolo-toys/releases/tag/v2.0.0
- [1.0.0]: https://github.com/LessUp/yolo-toys/releases/tag/v1.0.0
