"""
FastAPI 中间件 - 速率限制、超时控制、指标收集
"""

import logging
import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.metrics import HTTP_REQUEST_DURATION, update_memory_metric
from app.model_manager import get_memory_usage

logger = logging.getLogger(__name__)


class TimeoutMiddleware(BaseHTTPMiddleware):
    """请求超时中间件"""

    def __init__(self, app: ASGIApp, timeout_seconds: float = 60.0):
        super().__init__(app)
        self.timeout = timeout_seconds

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Note: Python's asyncio doesn't support true per-request cancellation
        # This is a simplified implementation
        start_time = time.time()
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            if duration > self.timeout:
                logger.warning(
                    "Request to %s took %.2fs (timeout: %.2fs)",
                    request.url.path,
                    duration,
                    self.timeout,
                )
            return response
        except Exception as e:
            logger.error("Request failed: %s", e)
            raise


class MetricsMiddleware(BaseHTTPMiddleware):
    """Prometheus 指标收集中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            raise
        finally:
            duration = time.time() - start_time
            HTTP_REQUEST_DURATION.labels(
                method=request.method, endpoint=request.url.path, status_code=str(status_code)
            ).observe(duration)

            # Update memory metric periodically
            if int(time.time()) % 10 == 0:
                update_memory_metric(get_memory_usage())

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全响应头中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Only add HSTS in production (HTTPS)
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """简单的内存速率限制中间件（生产环境建议使用 Redis）"""

    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        # Clean old requests
        if client_ip in self.requests:
            self.requests[client_ip] = [
                t for t in self.requests[client_ip] if current_time - t < 60
            ]
        else:
            self.requests[client_ip] = []

        # Check rate limit
        if len(self.requests.get(client_ip, [])) >= self.requests_per_minute:
            logger.warning("Rate limit exceeded for %s", client_ip)
            from starlette.responses import JSONResponse

            return JSONResponse(
                status_code=429, content={"detail": "Rate limit exceeded. Try again later."}
            )

        self.requests[client_ip].append(current_time)
        return await call_next(request)
