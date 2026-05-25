from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def api_success(data: Any) -> dict[str, Any]:
    return {
        "success": True,
        "data": data,
        "error": None,
        "timestamp": utc_timestamp(),
    }


def api_error(message: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "data": None,
            "error": message,
            "timestamp": utc_timestamp(),
        },
    )


def raise_api_error(message: str, status_code: int = 400) -> None:
    raise HTTPException(status_code=status_code, detail=message)


def validation_api_error(exc: RequestValidationError) -> JSONResponse:
    messages = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error.get("loc", []) if part != "body")
        message = error.get("msg", "Invalid request")
        messages.append(f"{location}: {message}" if location else message)
    return api_error("; ".join(messages) or "Invalid request", 422)


def paginated(items: list[Any], total: int, page: int, page_size: int) -> dict[str, Any]:
    return {
        "items": items,
        "total": total,
        "page": page,
        "pageSize": page_size,
    }
