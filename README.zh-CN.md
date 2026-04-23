# YOLO-Toys

> 一个把 **YOLOv8、DETR、OWL-ViT、Grounding DINO、BLIP** 统一到 FastAPI + WebSocket 接口下的多模型视觉推理平台。

[English](README.md) · [GitHub Pages](https://lessup.github.io/yolo-toys/) · [文档](https://lessup.github.io/yolo-toys/docs/) · [问题反馈](https://github.com/LessUp/yolo-toys/issues)

## 这个项目解决什么问题

YOLO-Toys 让多种视觉任务共用一套统一入口：

- 目标检测、实例分割、姿态估计
- 开放词汇 / 零样本文本检测
- 图像描述与视觉问答
- REST 推理与低延迟 WebSocket 流式推理

它适合用来：

- 快速比较不同视觉模型家族
- 搭建轻量视觉 demo / 后端
- 学习如何用统一 handler 架构整合混合模型栈

## 快速开始

### Docker

```bash
docker run -p 8000:8000 ghcr.io/lessup/yolo-toys:latest
```

然后打开 <http://localhost:8000>。

### 本地开发

```bash
git clone https://github.com/LessUp/yolo-toys.git
cd yolo-toys
bash scripts/dev.sh setup
. .venv/bin/activate
make run
```

## 你会得到什么

| 入口 | 作用 |
| --- | --- |
| `/infer` | 检测 / 分割 / 姿态 / 开放词汇推理 |
| `/caption` | BLIP 图像描述 |
| `/vqa` | BLIP 视觉问答 |
| `/models`, `/labels` | 模型发现 |
| `/ws` | 实时流式推理 |
| `/metrics`, `/health`, `/system/*` | 运维与可观测性 |

## 支持的模型家族

| 家族 | 示例 | 任务 |
| --- | --- | --- |
| YOLOv8 | `yolov8n.pt`、`yolov8n-seg.pt`、`yolov8n-pose.pt` | detect / segment / pose |
| DETR | `facebook/detr-resnet-50` | detect |
| OWL-ViT / Grounding DINO | `google/owlvit-base-patch32` | 零样本检测 |
| BLIP | `Salesforce/blip-image-captioning-base`、`Salesforce/blip-vqa-base` | caption / vqa |

## 仓库导航

| 路径 | 角色 |
| --- | --- |
| `app/` | 后端运行时 |
| `tests/` | pytest 测试 |
| `openspec/` | 当前规范与变更流程 |
| `docs/` | 长文档与参考资料 |
| 根目录 Jekyll 文件 | GitHub Pages 落地页与导航 |
| `.github/` | workflow、模板、Copilot 指令 |

## 开发流程

非简单修改统一走 **OpenSpec-first**：

1. 先探索或澄清
2. 创建 change proposal
3. 按 tasks 实施
4. 在阶段边界做 review
5. 完成后 archive

本地标准命令：

```bash
make lint
make format
make hooks
make typecheck
make test
```

## 下一步

- 想先看项目展示：进入 [GitHub Pages](https://lessup.github.io/yolo-toys/)
- 想看部署/API/架构：进入 [文档](https://lessup.github.io/yolo-toys/docs/)
- 想参与后续收尾或维护：看 [CONTRIBUTING.md](CONTRIBUTING.md)
