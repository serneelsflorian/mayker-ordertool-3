from typing import Any


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: list[Any] | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or []
        super().__init__(message)


class NotFoundError(AppException):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found", details: list[Any] | None = None) -> None:
        super().__init__(
            status_code=404,
            code="not_found",
            message=message,
            details=details,
        )


class AppValidationError(AppException):
    """Raised when business-level validation fails."""

    def __init__(self, message: str = "Validation error", details: list[Any] | None = None) -> None:
        super().__init__(
            status_code=422,
            code="validation_error",
            message=message,
            details=details,
        )
