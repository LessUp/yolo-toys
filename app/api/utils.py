"""
API 工具函数 - 图像处理、验证、解析
"""

import cv2
import numpy as np
from fastapi import HTTPException, UploadFile

from app.config import get_settings

settings = get_settings()

# 支持的图像类型魔术数字
ALLOWED_IMAGE_TYPES = {
    b"\xff\xd8\xff",  # JPEG
    b"\x89PNG\r\n\x1a\n",  # PNG
    b"GIF87a",  # GIF
    b"GIF89a",  # GIF
    b"RIFF",  # WebP (RIFF....WEBP)
    b"BM",  # BMP
}


def validate_image_mime(data: bytes) -> bool:
    """验证文件魔术数字（防止伪装扩展名攻击）"""
    if len(data) < 8:
        return False
    for magic in ALLOWED_IMAGE_TYPES:
        if data.startswith(magic):
            return True
    # Special check for WebP
    return bool(data.startswith(b"RIFF") and b"WEBP" in data[:12])


async def read_upload_image(file: UploadFile) -> tuple[np.ndarray, int]:
    """
    读取上传的图像文件，返回图像数组和文件大小

    Raises:
        HTTPException: 文件类型错误、空文件、过大或无法解码
    """
    if file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid content type, expected image/*")

    data = await file.read()
    file_size = len(data)

    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    if file_size > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large: {file_size} bytes (max: {settings.max_upload_bytes})",
        )

    # 安全验证：检查魔术数字
    if not validate_image_mime(data):
        raise HTTPException(status_code=400, detail="Invalid image file format")

    nparr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Failed to decode image")

    return img, file_size


def parse_optional_float(value: str | None) -> float | None:
    """Parse optional float from query param."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_optional_int(value: str | None) -> int | None:
    """Parse optional int from query param."""
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_text_queries(value: str | list[str] | None) -> list[str] | None:
    """Parse text queries from comma-separated string or list."""
    if value is None:
        return None
    if isinstance(value, str):
        queries = [q.strip() for q in value.split(",") if q.strip()]
        return queries or None
    queries = [str(q).strip() for q in value if str(q).strip()]
    return queries or None
