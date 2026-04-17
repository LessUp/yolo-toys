"""
应用配置 - 使用 Pydantic Settings 统一管理环境变量
"""

from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


def parse_bool_string(value: str | None) -> bool | None:
    if value is None:
        return None
    lowered = value.strip().lower()
    if lowered == "":
        return False
    if lowered in {"1", "true", "yes", "on"}:
        return True
    if lowered in {"0", "false", "no", "off"}:
        return False
    return None


class AppSettings(BaseSettings):
    """应用全局配置，从环境变量自动读取"""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # 服务
    port: int = Field(default=8000, alias="PORT")
    # 日志
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    # 模型
    model_name: str = Field(default="yolov8s.pt", alias="MODEL_NAME")
    conf_threshold: float = Field(default=0.25, alias="CONF_THRESHOLD")
    iou_threshold: float = Field(default=0.45, alias="IOU_THRESHOLD")
    max_det: int = Field(default=300, alias="MAX_DET")
    device: str = Field(default="", alias="DEVICE")
    skip_warmup: bool = Field(default=False, alias="SKIP_WARMUP")
    # BLIP/VQA 默认模型
    default_caption_model: str = Field(
        default="Salesforce/blip-image-captioning-base", alias="DEFAULT_CAPTION_MODEL"
    )
    default_vqa_model: str = Field(default="Salesforce/blip-vqa-base", alias="DEFAULT_VQA_MODEL")
    # BLIP 配置
    blip_max_tokens: int = Field(default=50, alias="BLIP_MAX_TOKENS")
    # Grounding DINO 配置
    grounding_text_threshold: float = Field(default=0.25, alias="GROUNDING_TEXT_THRESHOLD")
    # 预热配置
    warmup_image_size: int = Field(default=640, alias="WARMUP_IMAGE_SIZE")
    # GZip 配置
    gzip_min_size: int = Field(default=1000, alias="GZIP_MIN_SIZE")
    # CORS
    allow_origins: str = Field(default="*", alias="ALLOW_ORIGINS")
    # 限制
    max_upload_mb: int = Field(default=10, alias="MAX_UPLOAD_MB")
    max_concurrency: int = Field(default=4, alias="MAX_CONCURRENCY")

    @field_validator("log_level", mode="before")
    @classmethod
    def _validate_log_level(cls, v: Any) -> str:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if isinstance(v, str):
            upper = v.strip().upper()
            if upper in valid_levels:
                return upper
        return "INFO"

    @field_validator("skip_warmup", mode="before")
    @classmethod
    def _parse_skip_warmup(cls, v: Any):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            parsed = parse_bool_string(v)
            if parsed is None:
                raise ValueError("SKIP_WARMUP must be a boolean value")
            return parsed
        return bool(v)

    @property
    def origins_list(self) -> list[str]:
        raw = self.allow_origins.strip()
        if raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
