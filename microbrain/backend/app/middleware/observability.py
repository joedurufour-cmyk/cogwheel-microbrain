import json
import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logging.basicConfig(format="%(message)s", level=logging.INFO)
_log = logging.getLogger("microbrain")


class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = uuid.uuid4().hex[:10]
        request.state.trace_id = trace_id
        t0 = time.perf_counter()

        try:
            response = await call_next(request)
            _emit(trace_id, request, response.status_code, t0)
            response.headers["x-trace-id"] = trace_id
            return response
        except Exception as exc:
            _emit(trace_id, request, 500, t0, error=str(exc))
            raise


def _emit(trace_id: str, request: Request, status: int, t0: float, error: str | None = None) -> None:
    record: dict = {
        "trace_id": trace_id,
        "method": request.method,
        "path": request.url.path,
        "status": status,
        "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
    }
    if error:
        record["error"] = error
    if status >= 500:
        _log.error(json.dumps(record))
    else:
        _log.info(json.dumps(record))
