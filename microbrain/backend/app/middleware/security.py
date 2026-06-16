import os
import time
from collections import defaultdict

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
MAX_INPUT_BYTES = int(os.getenv("MAX_INPUT_BYTES", "8192"))
API_KEY = os.getenv("API_KEY", "")

_SKIP_AUTH = {"/health", "/docs", "/openapi.json", "/redoc"}

_buckets: dict[str, list[float]] = defaultdict(list)


class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in _SKIP_AUTH:
            return await call_next(request)

        # Input size guard
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_INPUT_BYTES:
            return JSONResponse({"error": "payload_too_large"}, status_code=413)

        # API key guard (opt-in: only enforced if API_KEY is set)
        if API_KEY:
            if request.headers.get("x-api-key", "") != API_KEY:
                return JSONResponse({"error": "unauthorized"}, status_code=401)

        # Per-IP rate limit
        ip = (request.client.host if request.client else "unknown")
        now = time.monotonic()
        window = [t for t in _buckets[ip] if now - t < 60.0]
        if len(window) >= RATE_LIMIT_PER_MINUTE:
            return JSONResponse(
                {"error": "rate_limit_exceeded", "retry_after_seconds": 60},
                status_code=429,
            )
        window.append(now)
        _buckets[ip] = window

        return await call_next(request)
