from typing import Any, Literal

from pydantic import BaseModel, Field


class Detection(BaseModel):
    bbox: list[float]
    score: float
    label: str
    polygons: list[list[float]] | None = None
    keypoints: list[list[float]] | None = None


class InferenceResponse(BaseModel):
    width: int
    height: int
    detections: list[Detection] = Field(default_factory=list)
    inference_time: float
    task: Literal["detect", "segment", "pose", "caption", "vqa"]
    caption: str | None = None
    question: str | None = None
    answer: str | None = None
    text_queries: list[str] | None = None
    model: str | None = None
    params: dict[str, Any] | None = None
