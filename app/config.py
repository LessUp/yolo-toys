"""
应用配置 - 使用 Pydantic Settings 统一管理环境变量
"""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """应用全局配置，从环境变量自动读取"""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # 服务
    port: int = Field(default=8000, alias="PORT")
    # 模型
    model_name: str = Field(default="yolov8s.pt", alias="MODEL_NAME")
    conf_threshold: float = Field(default=0.25, alias="CONF_THRESHOLD")
    iou_threshold: float = Field(default=0.45, alias="IOU_THRESHOLD")
    max_det: int = Field(default=300, alias="MAX_DET")
    device: str = Field(default="", alias="DEVICE")
    skip_warmup: bool = Field(default=False, alias="SKIP_WARMUP")
    # CORS
    allow_origins: str = Field(default="*", alias="ALLOW_ORIGINS")
    # 限制
    max_upload_mb: int = Field(default=10, alias="MAX_UPLOAD_MB")
    max_concurrency: int = Field(default=4, alias="MAX_CONCURRENCY")

    @field_validator("skip_warmup", mode="before")
    @classmethod
    def _parse_skip_warmup(cls, v):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return bool(v.strip())
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
