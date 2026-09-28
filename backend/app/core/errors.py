from typing import Any, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from app.core.logging import logger


class SentinelException(Exception):
    """Base application exception for SentinelForge."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


class UnauthorizedException(SentinelException):
    def __init__(self, message: str = "Authentication required or invalid credentials"):
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenException(SentinelException):
    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(
            code="FORBIDDEN",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class NotFoundException(SentinelException):
    def __init__(self, resource: str = "Resource", identifier: Optional[str] = None):
        msg = f"{resource} not found" if not identifier else f"{resource} '{identifier}' not found"
        super().__init__(
            code="NOT_FOUND",
            message=msg,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ConflictException(SentinelException):
    def __init__(self, message: str = "A conflicting resource already exists"):
        super().__init__(
            code="CONFLICT",
            message=message,
            status_code=status.HTTP_409_CONFLICT,
        )


class RateLimitException(SentinelException):
    def __init__(self, message: str = "Rate limit exceeded. Please retry later"):
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


async def sentinel_exception_handler(request: Request, exc: SentinelException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(
        f"Handled application exception: {exc.code} - {exc.message}",
        extra={"request_id": request_id, "status_code": exc.status_code}
    )
    content = {
        "error": {
            "code": exc.code,
            "message": exc.message,
            "request_id": request_id,
        }
    }
    if exc.details:
        content["error"]["details"] = exc.details
    return JSONResponse(status_code=exc.status_code, content=content)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    # Log the full exception internally, but never expose it to client
    logger.error(
        f"Unhandled server exception: {str(exc)}",
        exc_info=True,
        extra={"request_id": request_id}
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected security system error occurred. Reference the request ID.",
                "request_id": request_id,
            }
        },
    )
