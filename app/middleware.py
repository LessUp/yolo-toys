"""
FastAPI 中间件 - 速率限制、超时控制、指标收集
"""

import logging
import threading
import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
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
        status_code = 500

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
        self._lock = threading.Lock()
        self._last_cleanup = time.time()
        self._max_ips = 10000  # 最大跟踪 IP 数量限制

    def _cleanup_expired_ips(self, current_time: float) -> None:
        """定期清理过期 IP 记录，防止内存泄漏"""
        with self._lock:
            # 每 60 秒清理一次
            if current_time - self._last_cleanup < 60:
                return

            expired_ips = []
            for ip, timestamps in self.requests.items():
                # 过滤掉 60 秒前的请求
                self.requests[ip] = [t for t in timestamps if current_time - t < 60]
                if not self.requests[ip]:
                    expired_ips.append(ip)

            # 删除空 IP 记录
            for ip in expired_ips:
                del self.requests[ip]

            # 如果 IP 数量超过限制，删除最旧的 IP
            if len(self.requests) > self._max_ips:
                # 按 IP 的最后请求时间排序，删除最旧的
                sorted_ips = sorted(
                    self.requests.keys(),
                    key=lambda x: self.requests[x][-1] if self.requests[x] else 0,
                )
                for ip in sorted_ips[: len(self.requests) - self._max_ips]:
                    del self.requests[ip]

            self._last_cleanup = current_time
            logger.debug(
                "Rate limit cleanup: %d IPs tracked, %d expired removed",
                len(self.requests),
                len(expired_ips),
            )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        # 定期清理过期记录
        self._cleanup_expired_ips(current_time)

        with self._lock:
            # Clean old requests for this IP
            if client_ip in self.requests:
                self.requests[client_ip] = [
                    t for t in self.requests[client_ip] if current_time - t < 60
                ]
            else:
                self.requests[client_ip] = []

            # Check rate limit
            if len(self.requests.get(client_ip, [])) >= self.requests_per_minute:
                logger.warning("Rate limit exceeded for %s", client_ip)
                return JSONResponse(
                    status_code=429, content={"detail": "Rate limit exceeded. Try again later."}
                )

            self.requests[client_ip].append(current_time)

        return await call_next(request)
