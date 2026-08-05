from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "APPLICATION_ERROR",
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
            },
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
            },
        },
    )

class UnsupportedFileTypeException(AppException):
    def __init__(self):
        super().__init__(
            message="Only PDF, TXT, CSV and XLSX files are supported.",
            status_code=400,
            error_code="UNSUPPORTED_FILE_TYPE",
        )


class InvalidContentTypeException(AppException):
    def __init__(self):
        super().__init__(
            message="Invalid content type.",
            status_code=400,
            error_code="INVALID_CONTENT_TYPE",
        )


class FileTooLargeException(AppException):
    def __init__(self, max_size_mb: int):
        super().__init__(
            message=f"Maximum upload size is {max_size_mb} MB.",
            status_code=400,
            error_code="FILE_TOO_LARGE",
        )


class EmptyFileException(AppException):
    def __init__(self):
        super().__init__(
            message="Uploaded file is empty.",
            status_code=400,
            error_code="EMPTY_FILE",
        )