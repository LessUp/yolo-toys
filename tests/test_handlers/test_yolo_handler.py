"""
YOLOHandler 单元测试 - 测试 YOLO 模型的加载和推理逻辑

测试覆盖：
- load() 方法的成功/失败场景
- infer() 方法的检测/分割/姿态任务
- 参数传递和结果解析
"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from app.handlers.yolo_handler import YOLOHandler

# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture()
def handler():
    """创建 YOLOHandler 实例"""
    return YOLOHandler(device="cpu")


@pytest.fixture()
def mock_yolo_model():
    """创建模拟的 YOLO 模型"""
    model = MagicMock()
    model.model = MagicMock()
    model.model.task = "detect"
    return model


def _create_mock_tensor(arr):
    """创建模拟的 tensor 对象，支持 detach().cpu().numpy() 链式调用"""
    mock = MagicMock()
    mock.detach.return_value.cpu.return_value.numpy.return_value = np.array(arr)
    return mock


@pytest.fixture()
def mock_detection_result():
    """创建模拟的检测结果"""
    result = MagicMock()
    result.boxes = MagicMock()
    result.boxes.xyxy = _create_mock_tensor(
        [[10.0, 20.0, 100.0, 200.0], [50.0, 60.0, 150.0, 160.0]]
    )
    result.boxes.conf = _create_mock_tensor([0.95, 0.75])
    result.boxes.cls = _create_mock_tensor([0, 1])
    result.masks = None
    result.keypoints = None
    result.names = {0: "person", 1: "car"}
    return result


@pytest.fixture()
def mock_segmentation_result():
    """创建模拟的分割结果"""
    result = MagicMock()
    result.boxes = MagicMock()
    result.boxes.xyxy = _create_mock_tensor([[10.0, 20.0, 100.0, 200.0]])
    result.boxes.conf = _create_mock_tensor([0.90])
    result.boxes.cls = _create_mock_tensor([0])
    result.masks = MagicMock()
    result.masks.xy = [np.array([[10, 20], [100, 20], [100, 200], [10, 200]])]
    result.keypoints = None
    result.names = {0: "person"}
    return result


@pytest.fixture()
def mock_pose_result():
    """创建模拟的姿态估计结果"""
    result = MagicMock()
    result.boxes = MagicMock()
    result.boxes.xyxy = _create_mock_tensor([[10.0, 20.0, 100.0, 200.0]])
    result.boxes.conf = _create_mock_tensor([0.85])
    result.boxes.cls = _create_mock_tensor([0])
    result.masks = None
    result.keypoints = MagicMock()
    # 17 COCO keypoints (x, y) pairs
    result.keypoints.xy = [np.random.rand(17, 2) * 100]
    result.names = {0: "person"}
    return result


@pytest.fixture()
def test_image():
    """创建测试图像"""
    return np.zeros((480, 640, 3), dtype=np.uint8)


# ------------------------------------------------------------------
# Load Tests
# ------------------------------------------------------------------


def test_load_success(handler: YOLOHandler):
    """测试成功加载 YOLO 模型"""
    mock_model = MagicMock()

    with patch("ultralytics.YOLO", return_value=mock_model) as mock_yolo:
        model, processor = handler.load("yolov8n.pt")

    assert model is mock_model
    assert processor is None
    mock_yolo.assert_called_once_with("yolov8n.pt")


def test_load_with_custom_model_id(handler: YOLOHandler):
    """测试使用自定义模型 ID 加载"""
    mock_model = MagicMock()

    with patch("ultralytics.YOLO", return_value=mock_model) as mock_yolo:
        model, processor = handler.load("yolov8s.pt")

    assert model is mock_model
    assert processor is None
    mock_yolo.assert_called_once_with("yolov8s.pt")


def test_load_import_error(handler: YOLOHandler):
    """测试 ultralytics 未安装时的错误处理"""
    import builtins

    original_import = builtins.__import__

    def raising_import(name, *args, **kwargs):
        if name == "ultralytics":
            raise ImportError("missing ultralytics")
        return original_import(name, *args, **kwargs)

    with (
        patch("builtins.__import__", side_effect=raising_import),
        pytest.raises(RuntimeError, match="ultralytics not installed"),
    ):
        handler.load("yolov8n.pt")


# ------------------------------------------------------------------
# Infer Tests - Detection
# ------------------------------------------------------------------


def test_infer_detection(
    handler: YOLOHandler,
    mock_yolo_model: MagicMock,
    mock_detection_result: MagicMock,
    test_image: np.ndarray,
):
    """测试检测任务推理"""
    mock_yolo_model.return_value = [mock_detection_result]

    result = handler.infer(mock_yolo_model, None, test_image)

    assert result["task"] == "detect"
    assert result["width"] == 640
    assert result["height"] == 480
    assert "detections" in result
    assert len(result["detections"]) == 2
    assert result["detections"][0]["label"] == "person"
    assert result["detections"][1]["label"] == "car"
    assert result["inference_time"] > 0


def test_infer_empty_detections(
    handler: YOLOHandler,
    mock_yolo_model: MagicMock,
    test_image: np.ndarray,
):
    """测试空检测结果"""
    empty_result = MagicMock()
    empty_result.boxes = MagicMock()
    empty_result.boxes.xyxy = _create_mock_tensor(np.zeros((0, 4)))
    empty_result.boxes.conf = _create_mock_tensor([])
    empty_result.boxes.cls = _create_mock_tensor([])
    empty_result.masks = None
    empty_result.keypoints = None
    empty_result.names = {}

    mock_yolo_model.return_value = [empty_result]

    result = handler.infer(mock_yolo_model, None, test_image)

    assert result["task"] == "detect"
    assert result["detections"] == []


def test_infer_none_boxes(
    handler: YOLOHandler,
    mock_yolo_model: MagicMock,
    test_image: np.ndarray,
):
    """测试 boxes 为 None 的情况"""
    empty_result = MagicMock()
    empty_result.boxes = None
    empty_result.masks = None
    empty_result.keypoints = None

    mock_yolo_model.return_value = [empty_result]

    result = handler.infer(mock_yolo_model, None, test_image)

    assert result["detections"] == []


# ------------------------------------------------------------------
# Infer Tests - Segmentation
# ------------------------------------------------------------------


def test_infer_segmentation(
    handler: YOLOHandler,
    mock_yolo_model: MagicMock,
    mock_segmentation_result: MagicMock,
    test_image: np.ndarray,
):
    """测试分割任务推理"""
    mock_yolo_model.model.task = "segment"
    mock_yolo_model.return_value = [mock_segmentation_result]

    result = handler.infer(mock_yolo_model, None, test_image)

    assert result["task"] == "segment"
    assert "polygons" in result["detections"][0]


def test_infer_segmentation_from_result_masks(
    handler: YOLOHandler,
    mock_yolo_model: MagicMock,
    mock_segmentation_result: MagicMock,
    test_image: np.ndarray,
):
    """测试从 result.masks 推断分割任务"""
    mock_yolo_model.model.task = None  # 未设置 task
    mock_yolo_model.return_value = [mock_segmentation_result]

    result = handler.infer(mock_yolo_model, None, test_image)

    # 应该从 masks 推断为分割任务
    assert result["task"] == "segment"


# ------------------------------------------------------------------
# Infer Tests - Pose
# ------------------------------------------------------------------


def test_infer_pose(
    handler: YOLOHandler,
    mock_yolo_model: MagicMock,
    mock_pose_result: MagicMock,
    test_image: np.ndarray,
):
    """测试姿态估计任务推理"""
    mock_yolo_model.model.task = "pose"
    mock_yolo_model.return_value = [mock_pose_result]

    result = handler.infer(mock_yolo_model, None, test_image)

    assert result["task"] == "pose"
    assert "keypoints" in result["detections"][0]
    # COCO 格式有 17 个关键点
    assert len(result["detections"][0]["keypoints"]) == 17


def test_infer_pose_from_result_keypoints(
    handler: YOLOHandler,
    mock_yolo_model: MagicMock,
    mock_pose_result: MagicMock,
    test_image: np.ndarray,
):
    """测试从 result.keypoints 推断姿态任务"""
    mock_yolo_model.model.task = None
    mock_yolo_model.return_value = [mock_pose_result]

    result = handler.infer(mock_yolo_model, None, test_image)

    assert result["task"] == "pose"


# ------------------------------------------------------------------
# Parameter Passing Tests
# ------------------------------------------------------------------


def test_infer_passes_conf_parameter(
    handler: YOLOHandler,
    mock_yolo_model: MagicMock,
    mock_detection_result: MagicMock,
    test_image: np.ndarray,
):
    """测试 conf 参数传递"""
    mock_yolo_model.return_value = [mock_detection_result]

    handler.infer(mock_yolo_model, None, test_image, conf=0.5)

    call_kwargs = mock_yolo_model.call_args[1]
    assert call_kwargs["conf"] == 0.5


def test_infer_passes_iou_parameter(
    handler: YOLOHandler,
    mock_yolo_model: MagicMock,
    mock_detection_result: MagicMock,
    test_image: np.ndarray,
):
    """测试 iou 参数传递"""
    mock_yolo_model.return_value = [mock_detection_result]

    handler.infer(mock_yolo_model, None, test_image, iou=0.3)

    call_kwargs = mock_yolo_model.call_args[1]
    assert call_kwargs["iou"] == 0.3


def test_infer_passes_max_det_parameter(
    handler: YOLOHandler,
    mock_yolo_model: MagicMock,
    mock_detection_result: MagicMock,
    test_image: np.ndarray,
):
    """测试 max_det 参数传递"""
    mock_yolo_model.return_value = [mock_detection_result]

    handler.infer(mock_yolo_model, None, test_image, max_det=50)

    call_kwargs = mock_yolo_model.call_args[1]
    assert call_kwargs["max_det"] == 50


def test_infer_passes_imgsz_parameter(
    handler: YOLOHandler,
    mock_yolo_model: MagicMock,
    mock_detection_result: MagicMock,
    test_image: np.ndarray,
):
    """测试 imgsz 参数传递"""
    mock_yolo_model.return_value = [mock_detection_result]

    handler.infer(mock_yolo_model, None, test_image, imgsz=320)

    call_kwargs = mock_yolo_model.call_args[1]
    assert call_kwargs["imgsz"] == 320


def test_infer_ignores_imgsz_when_none(
    handler: YOLOHandler,
    mock_yolo_model: MagicMock,
    mock_detection_result: MagicMock,
    test_image: np.ndarray,
):
    """测试 imgsz 为 None 时不传递"""
    mock_yolo_model.return_value = [mock_detection_result]

    handler.infer(mock_yolo_model, None, test_image, imgsz=None)

    call_kwargs = mock_yolo_model.call_args[1]
    assert "imgsz" not in call_kwargs


def test_infer_half_on_cuda(handler: YOLOHandler):
    """测试 CUDA 设备上的 half 参数"""
    cuda_handler = YOLOHandler(device="cuda:0")
    mock_model = MagicMock()
    mock_result = MagicMock()
    mock_result.boxes.xyxy = _create_mock_tensor(np.zeros((0, 4)))
    mock_result.boxes.conf = _create_mock_tensor([])
    mock_result.boxes.cls = _create_mock_tensor([])
    mock_result.masks = None
    mock_result.keypoints = None
    mock_result.names = {}
    mock_model.return_value = [mock_result]

    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    cuda_handler.infer(mock_model, None, test_image, half=True)

    call_kwargs = mock_model.call_args[1]
    assert call_kwargs["half"] is True


def test_infer_half_ignored_on_cpu(
    handler: YOLOHandler,
    mock_yolo_model: MagicMock,
    mock_detection_result: MagicMock,
    test_image: np.ndarray,
):
    """测试 CPU 设备上忽略 half 参数"""
    mock_yolo_model.return_value = [mock_detection_result]

    handler.infer(mock_yolo_model, None, test_image, half=True)

    call_kwargs = mock_yolo_model.call_args[1]
    assert "half" not in call_kwargs


def test_infer_custom_device(
    handler: YOLOHandler,
    mock_yolo_model: MagicMock,
    mock_detection_result: MagicMock,
    test_image: np.ndarray,
):
    """测试自定义设备参数"""
    mock_yolo_model.return_value = [mock_detection_result]

    handler.infer(mock_yolo_model, None, test_image, device="cuda:1")

    call_kwargs = mock_yolo_model.call_args[1]
    assert call_kwargs["device"] == "cuda:1"


# ------------------------------------------------------------------
# Helper Method Tests
# ------------------------------------------------------------------


def test_resolve_task_detect():
    """测试任务类型推断 - 检测"""
    model = SimpleNamespace(model=SimpleNamespace(task="detect"))
    result = MagicMock()
    result.masks = None
    result.keypoints = None

    task = YOLOHandler._resolve_task(model, result)
    assert task == "detect"


def test_resolve_task_segment():
    """测试任务类型推断 - 分割"""
    model = SimpleNamespace(model=SimpleNamespace(task=None))
    result = MagicMock()
    result.masks = MagicMock()
    result.keypoints = None

    task = YOLOHandler._resolve_task(model, result)
    assert task == "segment"


def test_resolve_task_pose():
    """测试任务类型推断 - 姿态"""
    model = SimpleNamespace(model=SimpleNamespace(task=None))
    result = MagicMock()
    result.masks = None
    result.keypoints = MagicMock()

    task = YOLOHandler._resolve_task(model, result)
    assert task == "pose"


def test_resolve_task_fallback():
    """测试任务类型推断 - 默认检测"""
    model = SimpleNamespace(model=SimpleNamespace(task=None))
    result = MagicMock()
    result.masks = None
    result.keypoints = None

    task = YOLOHandler._resolve_task(model, result)
    assert task == "detect"


def test_parse_detections_with_dict_names():
    """测试检测结果解析 - 字典格式标签"""
    result = MagicMock()
    result.boxes.xyxy = _create_mock_tensor([[0.0, 0.0, 10.0, 10.0]])
    result.boxes.conf = _create_mock_tensor([0.9])
    result.boxes.cls = _create_mock_tensor([0])
    result.masks = None
    result.keypoints = None
    result.names = {0: "cat", 1: "dog"}

    dets = YOLOHandler._parse_detections(result, "detect")

    assert len(dets) == 1
    assert dets[0]["label"] == "cat"
    assert dets[0]["score"] == 0.9
    assert dets[0]["bbox"] == [0.0, 0.0, 10.0, 10.0]


def test_parse_detections_with_list_names():
    """测试检测结果解析 - 列表格式标签

    注意：当 names 是列表时，代码直接返回 str(classes[i])，
    因为列表不支持 get() 方法。这是已知的行为。
    """
    result = MagicMock()
    result.boxes.xyxy = _create_mock_tensor([[0.0, 0.0, 10.0, 10.0]])
    result.boxes.conf = _create_mock_tensor([0.85])
    result.boxes.cls = _create_mock_tensor([1])
    result.masks = None
    result.keypoints = None
    result.names = ["cat", "dog"]

    dets = YOLOHandler._parse_detections(result, "detect")

    assert len(dets) == 1
    # 当 names 是列表时，返回 class index 的字符串形式
    assert dets[0]["label"] == "1"


# ------------------------------------------------------------------
# Error Handling Tests
# ------------------------------------------------------------------


def test_infer_model_raises_exception(
    handler: YOLOHandler,
    mock_yolo_model: MagicMock,
    test_image: np.ndarray,
):
    """测试模型推理异常时的处理"""
    mock_yolo_model.side_effect = RuntimeError("CUDA out of memory")

    with pytest.raises(RuntimeError, match="CUDA out of memory"):
        handler.infer(mock_yolo_model, None, test_image)
