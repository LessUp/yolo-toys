"""
API 路由定义 - 从 main.py 中提取，职责单一
"""
import asyncio
import json
import logging
from typing import Optional

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, Query, UploadFile, WebSocket, WebSocketDisconnect

from app.config import get_settings
from app.model_manager import model_manager
from app.schemas import InferenceResponse
from app import __version__ as VERSION

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


def _get_optional_float(value: Optional[str]) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _get_optional_int(value: Optional[str]) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _get_optional_bool(value: Optional[str]) -> Optional[bool]:
    if value is None or value == "":
        return None
    lowered = value.lower()
    if lowered in {"1", "true", "yes", "on"}:
        return True
    if lowered in {"0", "false", "no", "off"}:
        return False
    return None


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
    from app.handlers.registry import get_available_models

    return {
        "default": settings.model_name,
        "categories": get_available_models(),
    }


@router.get("/models/{model_id:path}")
async def model_info(model_id: str):
    """获取指定模型的详细信息"""
    from app.handlers.registry import get_model_info

    info = get_model_info(model_id)
    if not info:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"id": model_id, **info}


@router.get("/labels")
async def labels(model: Optional[str] = Query(default=None)):
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
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/infer", response_model=InferenceResponse, response_model_exclude_none=True)
async def infer(
    file: UploadFile = File(...),
    conf: Optional[float] = Query(default=None, description="置信度阈值"),
    iou: Optional[float] = Query(default=None, description="IoU 阈值"),
    device: Optional[str] = Query(default=None, description="设备 (cpu/cuda/mps)"),
    max_det: Optional[int] = Query(default=None, description="最大检测数"),
    model: Optional[str] = Query(default=None, description="模型 ID"),
    imgsz: Optional[int] = Query(default=None, description="推理尺寸"),
    half: Optional[bool] = Query(default=None, description="FP16 半精度"),
    text_queries: Optional[str] = Query(default=None, description="文本查询（用于开放词汇检测）"),
    question: Optional[str] = Query(default=None, description="问题（用于 VQA）"),
):
    """统一推理端点"""
    img = await _read_upload_image(file)
    model_id = model or settings.model_name

    queries = None
    if text_queries:
        queries = [q.strip() for q in text_queries.split(",") if q.strip()]

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
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.exception("推理异常: model=%s", model_id)
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/caption", response_model=InferenceResponse, response_model_exclude_none=True)
async def caption(
    file: UploadFile = File(...),
    model: Optional[str] = Query(default="Salesforce/blip-image-captioning-base"),
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
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.exception("Caption 推理异常: model=%s", model)
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/vqa", response_model=InferenceResponse, response_model_exclude_none=True)
async def vqa(
    file: UploadFile = File(...),
    question: str = Query(..., description="要问的问题"),
    model: Optional[str] = Query(default="Salesforce/blip-vqa-base"),
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
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.exception("VQA 推理异常: model=%s", model)
            raise HTTPException(status_code=500, detail=str(e))


# ------------------------------------------------------------------
# WebSocket 端点
# ------------------------------------------------------------------

@router.websocket("/ws")
async def websocket_infer(websocket: WebSocket):
    """WebSocket 实时推理"""
    params = websocket.query_params
    conf = _get_optional_float(params.get("conf")) or settings.conf_threshold
    iou = _get_optional_float(params.get("iou")) or settings.iou_threshold
    max_det = _get_optional_int(params.get("max_det")) or settings.max_det
    device = params.get("device") or None
    model_id = params.get("model") or settings.model_name
    imgsz = _get_optional_int(params.get("imgsz"))
    half = _get_optional_bool(params.get("half")) or False
    text_queries_str = params.get("text_queries") or ""
    question = params.get("question") or None

    text_queries = None
    if text_queries_str:
        text_queries = [q.strip() for q in text_queries_str.split(",") if q.strip()]

    await websocket.accept()
    await websocket.send_text(
        json.dumps(
            {
                "type": "ready",
                "message": "connected",
                "model": model_id,
                "device": model_manager.device,
            },
            ensure_ascii=False,
        )
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

            data = message.get("bytes")
            if data is None:
                text = message.get("text")
                if text:
                    try:
                        config = json.loads(text)
                        if config.get("type") == "config":
                            model_id = config.get("model", model_id)
                            conf = config.get("conf", conf)
                            iou = config.get("iou", iou)
                            max_det = config.get("max_det", max_det)
                            device = config.get("device", device)
                            imgsz = config.get("imgsz", imgsz)
                            half = config.get("half", half)
                            if config.get("text_queries"):
                                text_queries = config["text_queries"]
                            if config.get("question"):
                                question = config["question"]
                            await websocket.send_text(
                                json.dumps(
                                    {"type": "config_updated", "model": model_id},
                                    ensure_ascii=False,
                                )
                            )
                    except json.JSONDecodeError:
                        pass
                continue

            if len(data) > settings.max_upload_bytes:
                await websocket.send_text(
                    json.dumps({"type": "error", "detail": "file too large"}, ensure_ascii=False)
                )
                continue

            nparr = np.frombuffer(data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                await websocket.send_text(
                    json.dumps(
                        {"type": "error", "detail": "failed to decode image"}, ensure_ascii=False
                    )
                )
                continue

            try:
                async with semaphore:
                    result = await loop.run_in_executor(
                        None,
                        lambda: model_manager.infer(
                            model_id=model_id,
                            image=img,
                            conf=conf,
                            iou=iou,
                            max_det=max_det,
                            device=device,
                            imgsz=imgsz,
                            half=half,
                            text_queries=text_queries,
                            question=question,
                        ),
                    )
                result["model"] = model_id
            except Exception as exc:
                logger.warning("WS 推理异常: %s", exc)
                await websocket.send_text(
                    json.dumps({"type": "error", "detail": str(exc)}, ensure_ascii=False)
                )
                continue

            await websocket.send_text(
                json.dumps({"type": "result", "data": result}, ensure_ascii=False)
            )
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
