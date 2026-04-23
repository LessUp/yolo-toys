# Proposal: Improve Test Coverage

## Summary

提升 YOLO-Toys 项目的测试覆盖率从 65% 到 80%+，重点改进 handler 模块和 WebSocket 模块的测试覆盖。

## Motivation

当前测试覆盖率为 65.38%，但存在明显的覆盖盲区：

| 模块 | 当前覆盖率 | 问题 |
|------|-----------|------|
| YOLOHandler | 16% | 核心 YOLO 推理逻辑未测试 |
| HFHandler | 17% | HuggingFace 模型推理未测试 |
| BLIPHandler | 29% | 多模态推理部分覆盖 |
| WebSocket | 74% | 错误处理和边界情况未覆盖 |

这些问题可能导致：
- 模型推理逻辑变更时无法及时发现问题
- 错误处理路径存在未验证的 bug
- 重构时缺乏信心保障

## Goals

1. 将整体测试覆盖率提升至 80%+
2. Handler 模块覆盖率达到 60%+
3. WebSocket 模块覆盖率达到 85%+
4. 添加集成测试验证端到端推理流程

## Non-Goals

- 不修改生产代码逻辑
- 不添加新的 API 端点
- 不改变现有测试的结构

## Success Criteria

- `make test` 通过且覆盖率 >= 80%
- 所有新增测试有明确的测试目的注释
- 测试执行时间保持在 2 分钟以内
