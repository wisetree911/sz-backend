import time
from collections.abc import Callable

import structlog
from app.core.logging import (
    new_request_id,
    set_request_id,
)
from fastapi import Request, Response

log = structlog.get_logger("http")


async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
    rid = new_request_id()
    set_request_id(rid)

    started = time.perf_counter()
    try:
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - started) * 1000

        log.info(
            "request",
            request_id=rid,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(elapsed_ms, 2),
        )
        response.headers["x-request-id"] = rid
        return response

    except Exception:
        elapsed_ms = (time.perf_counter() - started) * 1000
        log.exception(
            "unhandled_exception",
            request_id=rid,
            method=request.method,
            path=request.url.path,
            duration_ms=round(elapsed_ms, 2),
        )
        raise
