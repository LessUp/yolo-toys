from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class Detection(BaseModel):
    bbox: List[float]
    score: float
    label: str
    polygons: Optional[List[List[float]]] = None
    keypoints: Optional[List[List[float]]] = None


class InferenceResponse(BaseModel):
    width: int
    height: int
    detections: List[Detection] = Field(default_factory=list)
    inference_time: float
    task: Literal["detect", "segment", "pose", "caption", "vqa"]
    caption: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    text_queries: Optional[List[str]] = None
    model: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
