import logging
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


def _error_response(code: str, message: str, details: list[Any]) -> JSONResponse:
    return JSONResponse(
        status_code=_status_from_code(code),
        content={"error": {"code": code, "message": message, "details": details}},
    )


def _status_from_code(code: str) -> int:
    mapping = {
        "not_found": 404,
        "validation_error": 422,
    }
    return mapping.get(code, 500)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.warning(
        "AppException: code=%s message=%s path=%s",
        exc.code,
        exc.message,
        request.url.path,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
    )


async def request_validation_exception_handler(
    request: Request, exc: PydanticValidationError
) -> JSONResponse:
    logger.debug("RequestValidationError at %s: %s", request.url.path, exc.errors())
    details = [
        {"loc": list(err["loc"]), "msg": err["msg"], "type": err["type"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "details": details,
            }
        },
    )
