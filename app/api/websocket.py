"""
WebSocket 实时推理路由

- /ws - WebSocket 实时推理连接
"""

import asyncio
import contextlib
import json
import logging
import time
from typing import Any

import cv2
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.datastructures import ImmutableMultiQueryDict

from app import __version__ as VERSION
from app.api.utils import parse_text_queries, validate_image_mime
from app.config import get_settings, parse_bool_string
from app.metrics import (
    INFERENCE_LATENCY,
    INFERENCE_REQUESTS,
    WEBSOCKET_CONNECTIONS,
    WEBSOCKET_MESSAGES,
)
from app.model_manager import model_manager

router = APIRouter(tags=["WebSocket"])
logger = logging.getLogger(__name__)
settings = get_settings()
semaphore = asyncio.Semaphore(settings.max_concurrency)


def _parse_ws_state(params: ImmutableMultiQueryDict) -> dict[str, Any]:
    """从 WebSocket query params 解析初始推理状态"""
    text_queries = parse_text_queries(params.get("text_queries"))
    conf = _get_optional_float(params.get("conf"))
    iou = _get_optional_float(params.get("iou"))
    max_det = _get_optional_int(params.get("max_det"))
    half = parse_bool_string(params.get("half"))
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


def _apply_ws_config(state: dict[str, Any], config: dict[str, Any]) -> None:
    """将客户端 config 消息合并到当前推理状态"""
    for key in ("model_id", "conf", "iou", "max_det", "device", "imgsz", "half"):
        cfg_key = "model" if key == "model_id" else key
        if cfg_key in config:
            state[key] = config[cfg_key]
    if "text_queries" in config:
        state["text_queries"] = parse_text_queries(config["text_queries"])
    if "question" in config:
        state["question"] = config["question"] or None


def _decode_ws_frame(data: bytes) -> np.ndarray | None:
    """解码 WebSocket 二进制帧为 OpenCV 图像"""
    if not validate_image_mime(data):
        return None
    nparr = np.frombuffer(data, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


async def _ws_send_json(websocket: WebSocket, payload: dict[str, Any]) -> None:
    """发送 JSON 消息"""
    await websocket.send_text(json.dumps(payload, ensure_ascii=False))


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


@router.websocket("/ws")
async def websocket_infer(websocket: WebSocket) -> None:
    """WebSocket 实时推理 - 增强版"""
    state = _parse_ws_state(websocket.query_params)
    logger.info("WebSocket 连接: model=%s, client=%s", state["model_id"], websocket.client)

    WEBSOCKET_CONNECTIONS.inc()
    WEBSOCKET_MESSAGES.labels(message_type="connection", direction="in").inc()

    await websocket.accept()
    await _ws_send_json(
        websocket,
        {
            "type": "ready",
            "message": "connected",
            "model": state["model_id"],
            "device": model_manager.device,
            "version": VERSION,
        },
    )
    WEBSOCKET_MESSAGES.labels(message_type="ready", direction="out").inc()

    loop = asyncio.get_running_loop()
    last_ping = time.time()

    try:
        while True:
            try:
                message = await asyncio.wait_for(websocket.receive(), timeout=60.0)
            except TimeoutError:
                if time.time() - last_ping > 30:
                    try:
                        await websocket.send_json({"type": "ping"})
                        last_ping = time.time()
                    except Exception:
                        break
                continue
            except WebSocketDisconnect:
                logger.debug("WebSocket 客户端断开连接")
                break
            except RuntimeError as e:
                logger.warning("WebSocket 运行时错误: %s", e)
                break

            if message.get("type") == "websocket.disconnect":
                logger.debug("WebSocket 收到断开消息")
                break

            # 心跳响应
            if message.get("type") == "websocket.ping":
                await websocket.send_json({"type": "pong"})
                continue

            # 文本消息：配置更新
            data = message.get("bytes")
            if data is None:
                text = message.get("text")
                if text:
                    try:
                        msg = json.loads(text)
                        if msg.get("type") == "config":
                            _apply_ws_config(state, msg)
                            logger.debug("WebSocket 配置更新: %s", msg)
                            await _ws_send_json(
                                websocket,
                                {
                                    "type": "config_updated",
                                    "model": state["model_id"],
                                },
                            )
                            WEBSOCKET_MESSAGES.labels(
                                message_type="config_updated", direction="out"
                            ).inc()
                        elif msg.get("type") == "ping":
                            await websocket.send_json({"type": "pong"})
                    except json.JSONDecodeError as e:
                        logger.warning("WebSocket JSON 解析失败: %s", e)
                        WEBSOCKET_MESSAGES.labels(message_type="error", direction="out").inc()
                continue

            # 二进制消息：图像帧
            WEBSOCKET_MESSAGES.labels(message_type="image", direction="in").inc()

            if len(data) > settings.max_upload_bytes:
                logger.warning("WebSocket 文件过大: %d bytes", len(data))
                await _ws_send_json(websocket, {"type": "error", "detail": "file too large"})
                WEBSOCKET_MESSAGES.labels(message_type="error", direction="out").inc()
                continue

            img = _decode_ws_frame(data)
            if img is None:
                logger.warning("WebSocket 图像解码失败或格式无效")
                await _ws_send_json(websocket, {"type": "error", "detail": "invalid image format"})
                WEBSOCKET_MESSAGES.labels(message_type="error", direction="out").inc()
                continue

            # 执行推理
            start_time = time.time()
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

                duration = time.time() - start_time
                INFERENCE_LATENCY.labels(
                    model=state["model_id"], task=result.get("task", "detect")
                ).observe(duration)
                INFERENCE_REQUESTS.labels(
                    model=state["model_id"], task=result.get("task", "detect"), status="success"
                ).inc()

            except Exception as exc:
                INFERENCE_REQUESTS.labels(
                    model=state["model_id"], task="unknown", status="error"
                ).inc()
                logger.warning("WebSocket 推理异常: model=%s, error=%s", state["model_id"], exc)
                await _ws_send_json(websocket, {"type": "error", "detail": str(exc)})
                WEBSOCKET_MESSAGES.labels(message_type="error", direction="out").inc()
                continue

            await _ws_send_json(websocket, {"type": "result", "data": result})
            WEBSOCKET_MESSAGES.labels(message_type="result", direction="out").inc()

    except Exception as e:
        logger.error("WebSocket 未处理异常: %s", e)
    finally:
        WEBSOCKET_CONNECTIONS.dec()
        with contextlib.suppress(Exception):
            await websocket.close()
        logger.info("WebSocket 连接关闭: client=%s", websocket.client)
