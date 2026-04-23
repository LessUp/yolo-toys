# Design: Improve Test Coverage

## Approach

采用分层测试策略，使用 mock 隔离外部依赖（模型加载、推理），专注于测试业务逻辑。

## Test Categories

### 1. Handler Unit Tests

使用 pytest + monkeypatch 模拟模型加载和推理：

```
tests/
├── test_handlers/
│   ├── test_yolo_handler.py    # YOLO 推理逻辑测试
│   ├── test_hf_handler.py      # HuggingFace 推理逻辑测试
│   └── test_blip_handler.py    # BLIP 推理逻辑测试
```

**Mock 策略**:
- 模拟 `YOLO()` 构造函数返回 mock model
- 模拟 `model()` 调用返回预设的 Results 对象
- 模拟 HuggingFace pipeline 返回预设结果

### 2. WebSocket Integration Tests

扩展现有 WebSocket 测试，覆盖：

- 错误处理路径（decode error, model not found, inference error）
- 边界情况（超大文件、无效参数、空帧）
- 心跳和超时机制
- 多客户端并发

### 3. Model Manager Tests

补充 ModelManager 的测试：

- 缓存命中/未命中场景
- TTL 过期清理
- 并发加载安全性

## Test Data

创建测试 fixtures：

```python
# tests/conftest.py

@pytest.fixture
def mock_yolo_model():
    """模拟 YOLO 模型返回检测框"""
    ...

@pytest.fixture
def mock_detr_pipeline():
    """模拟 DETR pipeline 返回检测结果"""
    ...

@pytest.fixture
def mock_blip_processor():
    """模拟 BLIP processor 和 model"""
    ...
```

## Implementation Notes

1. **隔离原则**: 测试不应依赖真实模型文件或 GPU
2. **速度优先**: 使用 mock 避免模型加载开销
3. **可读性**: 每个测试用例包含清晰的 docstring
4. **覆盖率精度**: 使用 `# pragma: no cover` 排除无法测试的代码路径

## File Changes

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `tests/test_handlers/` | 新增 | Handler 单元测试目录 |
| `tests/conftest.py` | 修改 | 添加共享 fixtures |
| `tests/test_api.py` | 修改 | 扩展 WebSocket 测试 |
| `tests/test_model_manager.py` | 新增 | ModelManager 专项测试 |
| `pyproject.toml` | 修改 | 提高覆盖率阈值到 80% |
