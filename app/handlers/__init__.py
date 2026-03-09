"""
模型处理器模块 - 策略模式
每种模型类型实现统一的 BaseHandler 接口
"""

from app.handlers.base import BaseHandler
from app.handlers.registry import HandlerRegistry

__all__ = ["BaseHandler", "HandlerRegistry"]
