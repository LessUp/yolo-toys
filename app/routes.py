"""
API 路由定义 - 从 main.py 中提取，职责单一
"""

import asyncio
import contextlib
import json
import logging

import cv2
import numpy as np
from fastapi import (
    APIRouter,
    File,
    HTTPException,
    Query,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)

from app import __version__ as VERSION
from app.config import get_settings, parse_bool_string
from app.handlers.registry import get_available_models, get_model_info
from app.model_manager import model_manager
from app.schemas import InferenceResponse

logger = logging.getLogger(__name__)

settings = get_settings()
semaphore = asyncio.Semaphore(settings.max_concurrency)

router = APIRouter()


# ------------------------------------------------------------------
# 工具函数
# ------------------------------------------------------------------


async def _read_upload_image(file: UploadFile) -> np.ndarray:
    if file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid content type")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="File too large")

    nparr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Failed to decode image")
    return img


def _get_optional_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _get_optional_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _get_optional_bool(value: str | None) -> bool | None:
    return parse_bool_string(value)


def _parse_text_queries(value: str | list[str] | None) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, str):
        queries = [q.strip() for q in value.split(",") if q.strip()]
        return queries or None
    queries = [str(q).strip() for q in value if str(q).strip()]
    return queries or None


# ------------------------------------------------------------------
# REST 端点
# ------------------------------------------------------------------


@router.get("/health")
async def health():
    """健康检查端点"""
    return {
        "status": "ok",
        "version": VERSION,
        "device": model_manager.device,
        "default_model": settings.model_name,
        "defaults": {
            "conf": settings.conf_threshold,
            "iou": settings.iou_threshold,
            "max_det": settings.max_det,
        },
    }


@router.get("/models")
async def list_models():
    """获取所有可用模型，按类别分组"""
    return {
        "default": settings.model_name,
        "categories": get_available_models(),
    }


@router.get("/models/{model_id:path}")
async def model_info(model_id: str):
    """获取指定模型的详细信息"""
    info = get_model_info(model_id)
    if not info:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"id": model_id, **info}


@router.get("/labels")
async def labels(model: str | None = Query(default=None)):
    """获取模型的标签列表"""
    model_id = model or settings.model_name
    try:
        m = model_manager.load_model(model_id)
        names = getattr(getattr(m, "model", None), "names", None)
        if isinstance(names, dict):
            ordered = [names[k] for k in sorted(names.keys())]
        elif isinstance(names, (list, tuple)):
            ordered = list(names)
        else:
            ordered = []
        return {"model": model_id, "labels": ordered}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/infer", response_model=InferenceResponse, response_model_exclude_none=True)
async def infer(
    file: UploadFile = File(...),
    conf: float | None = Query(default=None, description="置信度阈值"),
    iou: float | None = Query(default=None, description="IoU 阈值"),
    device: str | None = Query(default=None, description="设备 (cpu/cuda/mps)"),
    max_det: int | None = Query(default=None, description="最大检测数"),
    model: str | None = Query(default=None, description="模型 ID"),
    imgsz: int | None = Query(default=None, description="推理尺寸"),
    half: bool | None = Query(default=None, description="FP16 半精度"),
    text_queries: str | None = Query(default=None, description="文本查询（用于开放词汇检测）"),
    question: str | None = Query(default=None, description="问题（用于 VQA）"),
):
    """统一推理端点"""
    img = await _read_upload_image(file)
    model_id = model or settings.model_name

    queries = _parse_text_queries(text_queries)

    async with semaphore:
        try:
            result = await asyncio.to_thread(
                model_manager.infer,
                model_id=model_id,
                image=img,
                conf=conf if conf is not None else settings.conf_threshold,
                iou=iou if iou is not None else settings.iou_threshold,
                max_det=max_det if max_det is not None else settings.max_det,
                device=device,
                imgsz=imgsz,
                half=half if half is not None else False,
                text_queries=queries,
                question=question,
            )
            result["model"] = model_id
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except Exception as e:
            logger.exception("推理异常: model=%s", model_id)
            raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/caption", response_model=InferenceResponse, response_model_exclude_none=True)
async def caption(
    file: UploadFile = File(...),
    model: str | None = Query(default="Salesforce/blip-image-captioning-base"),
):
    """图像描述生成"""
    img = await _read_upload_image(file)

    async with semaphore:
        try:
            result = await asyncio.to_thread(
                model_manager.infer,
                model_id=model,
                image=img,
            )
            result["model"] = model
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except Exception as e:
            logger.exception("Caption 推理异常: model=%s", model)
            raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/vqa", response_model=InferenceResponse, response_model_exclude_none=True)
async def vqa(
    file: UploadFile = File(...),
    question: str = Query(..., description="要问的问题"),
    model: str | None = Query(default="Salesforce/blip-vqa-base"),
):
    """视觉问答"""
    img = await _read_upload_image(file)

    async with semaphore:
        try:
            result = await asyncio.to_thread(
                model_manager.infer,
                model_id=model,
                image=img,
                question=question,
            )
            result["model"] = model
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except Exception as e:
            logger.exception("VQA 推理异常: model=%s", model)
            raise HTTPException(status_code=500, detail=str(e)) from e


# ------------------------------------------------------------------
# WebSocket 端点
# ------------------------------------------------------------------


def _parse_ws_state(params) -> dict:
    """从 WebSocket query params 解析初始推理状态"""
    text_queries = _parse_text_queries(params.get("text_queries"))
    conf = _get_optional_float(params.get("conf"))
    iou = _get_optional_float(params.get("iou"))
    max_det = _get_optional_int(params.get("max_det"))
    half = _get_optional_bool(params.get("half"))
    return {
        "model_id": params.get("model") or settings.model_name,
        "conf": conf if conf is not None else settings.conf_threshold,
        "iou": iou if iou is not None else settings.iou_threshold,
        "max_det": max_det if max_det is not None else settings.max_det,
        "device": params.get("device") or None,
        "imgsz": _get_optional_int(params.get("imgsz")),
        "half": half if half is not None else False,
        "text_queries": text_queries,
        "question": params.get("question") or None,
    }


def _apply_ws_config(state: dict, config: dict) -> None:
    """将客户端 config 消息合并到当前推理状态"""
    for key in ("model_id", "conf", "iou", "max_det", "device", "imgsz", "half"):
        cfg_key = "model" if key == "model_id" else key
        if cfg_key in config:
            state[key] = config[cfg_key]
    if "text_queries" in config:
        state["text_queries"] = _parse_text_queries(config["text_queries"])
    if "question" in config:
        state["question"] = config["question"] or None


def _decode_ws_frame(data: bytes) -> np.ndarray | None:
    """解码 WebSocket 二进制帧为 OpenCV 图像"""
    nparr = np.frombuffer(data, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


async def _ws_send_json(websocket: WebSocket, payload: dict) -> None:
    """发送 JSON 消息"""
    await websocket.send_text(json.dumps(payload, ensure_ascii=False))


@router.websocket("/ws")
async def websocket_infer(websocket: WebSocket):
    """WebSocket 实时推理"""
    state = _parse_ws_state(websocket.query_params)

    await websocket.accept()
    await _ws_send_json(
        websocket,
        {
            "type": "ready",
            "message": "connected",
            "model": state["model_id"],
            "device": model_manager.device,
        },
    )

    loop = asyncio.get_running_loop()

    try:
        while True:
            try:
                message = await websocket.receive()
            except (WebSocketDisconnect, RuntimeError):
                break

            if message.get("type") == "websocket.disconnect":
                break

            # --- 文本消息：配置更新 ---
            data = message.get("bytes")
            if data is None:
                text = message.get("text")
                if text:
                    try:
                        config = json.loads(text)
                        if config.get("type") == "config":
                            _apply_ws_config(state, config)
                            await _ws_send_json(
                                websocket,
                                {
                                    "type": "config_updated",
                                    "model": state["model_id"],
                                },
                            )
                    except json.JSONDecodeError:
                        pass
                continue

            # --- 二进制消息：图像帧 ---
            if len(data) > settings.max_upload_bytes:
                await _ws_send_json(websocket, {"type": "error", "detail": "file too large"})
                continue

            img = _decode_ws_frame(data)
            if img is None:
                await _ws_send_json(
                    websocket, {"type": "error", "detail": "failed to decode image"}
                )
                continue

            try:
                async with semaphore:
                    result = await loop.run_in_executor(
                        None,
                        lambda s=state, i=img: model_manager.infer(
                            model_id=s["model_id"],
                            image=i,
                            conf=s["conf"],
                            iou=s["iou"],
                            max_det=s["max_det"],
                            device=s["device"],
                            imgsz=s["imgsz"],
                            half=s["half"],
                            text_queries=s["text_queries"],
                            question=s["question"],
                        ),
                    )
                result["model"] = state["model_id"]
            except Exception as exc:
                logger.warning("WS 推理异常: %s", exc)
                await _ws_send_json(websocket, {"type": "error", "detail": str(exc)})
                continue

            await _ws_send_json(websocket, {"type": "result", "data": result})
    finally:
        with contextlib.suppress(Exception):
            await websocket.close()
