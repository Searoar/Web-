"""统一 JSON 错误体：与 FastAPI 默认 {\"detail\": ...} 区分，便于报告说明。"""

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status


def _status_to_code(s: int) -> str:
    return {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        422: "validation_error",
        500: "internal_error",
    }.get(s, "http_error")


async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    d = exc.detail
    if isinstance(d, dict) and "error" in d:
        body = d
    else:
        msg = d if isinstance(d, str) else str(d)
        body = {"error": {"code": _status_to_code(exc.status_code), "message": msg}}
    return JSONResponse(status_code=exc.status_code, content=body)


async def request_validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request body or query validation failed",
                "errors": exc.errors(),
            }
        },
    )
