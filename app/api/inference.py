"""
推理 API 路由

- /infer - 通用推理
- /caption - 图像描述
- /vqa - 视觉问答
"""

import asyncio
import logging
import time

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.api.utils import parse_text_queries, read_upload_image
from app.config import get_settings
from app.metrics import INFERENCE_INPUT_SIZE, INFERENCE_LATENCY, INFERENCE_REQUESTS
from app.model_manager import model_manager
from app.schemas import InferenceResponse

router = APIRouter(tags=["Inference"])
logger = logging.getLogger(__name__)
settings = get_settings()
semaphore = asyncio.Semaphore(settings.max_concurrency)


@router.post("/infer", response_model=InferenceResponse, response_model_exclude_none=True)
async def infer(
    file: UploadFile = File(...),
    conf: float | None = Query(default=None, ge=0.0, le=1.0, description="置信度阈值 (0.0-1.0)"),
    iou: float | None = Query(default=None, ge=0.0, le=1.0, description="IoU 阈值 (0.0-1.0)"),
    device: str | None = Query(default=None, description="设备 (cpu/cuda/mps)"),
    max_det: int | None = Query(default=None, gt=0, le=1000, description="最大检测数 (1-1000)"),
    model: str | None = Query(default=None, description="模型 ID"),
    imgsz: int | None = Query(default=None, ge=32, le=4096, description="推理尺寸 (32-4096)"),
    half: bool | None = Query(default=None, description="FP16 半精度"),
    text_queries: str | None = Query(
        default=None, description="文本查询（用于开放词汇检测，逗号分隔）"
    ),
    question: str | None = Query(default=None, max_length=500, description="问题（用于 VQA）"),
):
    """统一推理端点 - 支持检测、分割、姿态估计、开放词汇检测、VQA"""
    start_time = time.time()
    img, file_size = await read_upload_image(file)
    model_id = model or settings.model_name
    queries = parse_text_queries(text_queries)

    INFERENCE_INPUT_SIZE.observe(file_size)

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

            duration = time.time() - start_time
            INFERENCE_LATENCY.labels(model=model_id, task=result.get("task", "detect")).observe(
                duration
            )
            INFERENCE_REQUESTS.labels(
                model=model_id, task=result.get("task", "detect"), status="success"
            ).inc()

            return result
        except ValueError as e:
            INFERENCE_REQUESTS.labels(model=model_id, task="unknown", status="error").inc()
            raise HTTPException(status_code=400, detail=str(e)) from e
        except RuntimeError as e:
            INFERENCE_REQUESTS.labels(model=model_id, task="unknown", status="error").inc()
            logger.error("Inference runtime error for model %s: %s", model_id, e)
            raise HTTPException(status_code=500, detail=f"Model inference failed: {e}") from e
        except Exception as e:
            INFERENCE_REQUESTS.labels(model=model_id, task="unknown", status="error").inc()
            logger.exception("Unexpected inference error for model %s", model_id)
            raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/caption", response_model=InferenceResponse, response_model_exclude_none=True)
async def caption(
    file: UploadFile = File(...),
    model: str | None = Query(default=None, description="模型 ID"),
):
    """图像描述生成"""
    start_time = time.time()
    img, file_size = await read_upload_image(file)
    model_id = model or settings.default_caption_model

    INFERENCE_INPUT_SIZE.observe(file_size)

    async with semaphore:
        try:
            result = await asyncio.to_thread(
                model_manager.infer,
                model_id=model_id,
                image=img,
            )
            result["model"] = model_id

            duration = time.time() - start_time
            INFERENCE_LATENCY.labels(model=model_id, task="caption").observe(duration)
            INFERENCE_REQUESTS.labels(model=model_id, task="caption", status="success").inc()

            return result
        except ValueError as e:
            INFERENCE_REQUESTS.labels(model=model_id, task="caption", status="error").inc()
            raise HTTPException(status_code=400, detail=str(e)) from e
        except Exception as e:
            INFERENCE_REQUESTS.labels(model=model_id, task="caption", status="error").inc()
            raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/vqa", response_model=InferenceResponse, response_model_exclude_none=True)
async def vqa(
    file: UploadFile = File(...),
    question: str = Query(..., description="要问的问题"),
    model: str | None = Query(default=None, description="模型 ID"),
):
    """视觉问答"""
    start_time = time.time()
    img, file_size = await read_upload_image(file)
    model_id = model or settings.default_vqa_model

    INFERENCE_INPUT_SIZE.observe(file_size)

    async with semaphore:
        try:
            result = await asyncio.to_thread(
                model_manager.infer,
                model_id=model_id,
                image=img,
                question=question,
            )
            result["model"] = model_id

            duration = time.time() - start_time
            INFERENCE_LATENCY.labels(model=model_id, task="vqa").observe(duration)
            INFERENCE_REQUESTS.labels(model=model_id, task="vqa", status="success").inc()

            return result
        except ValueError as e:
            INFERENCE_REQUESTS.labels(model=model_id, task="vqa", status="error").inc()
            raise HTTPException(status_code=400, detail=str(e)) from e
        except Exception as e:
            INFERENCE_REQUESTS.labels(model=model_id, task="vqa", status="error").inc()
            raise HTTPException(status_code=500, detail=str(e)) from e
