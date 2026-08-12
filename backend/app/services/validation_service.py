from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import (
    EmptyFileException,
    FileTooLargeException,
    InvalidContentTypeException,
    UnsupportedFileTypeException,
)
from app.core.logging import logger


class ValidationService:
    """
    Validates uploaded documents before storage.
    """

    async def validate(self, file: UploadFile) -> None:
        """
        Validate an uploaded file.

        Raises:
            UnsupportedFileTypeException
            InvalidContentTypeException
            EmptyFileException
            FileTooLargeException
        """

        logger.info("Validating file: %s", file.filename)

        # -------------------------
        # Extension Validation
        # -------------------------
        extension = Path(file.filename).suffix.lower()

        if extension not in settings.ALLOWED_EXTENSIONS:
            logger.warning(
                "Unsupported extension: %s",
                extension,
            )
            raise UnsupportedFileTypeException()

        logger.info("Extension validation passed")

        # -------------------------
        # Content Type Validation
        # -------------------------
        if file.content_type not in settings.ALLOWED_CONTENT_TYPES:
            logger.warning(
                "Invalid content type: %s",
                file.content_type,
            )
            raise InvalidContentTypeException()

        logger.info("Content type validation passed")

        # -------------------------
        # File Size Validation
        # -------------------------
        contents = await file.read()

        size = len(contents)

        if size == 0:
            logger.warning("Empty file uploaded")
            raise EmptyFileException()

        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

        if size > max_size:
            logger.warning(
                "File exceeds maximum size (%s bytes)",
                size,
            )
            raise FileTooLargeException(
                settings.MAX_UPLOAD_SIZE_MB
            )

        logger.info(
            "File size validation passed (%s bytes)",
            size,
        )

        # Reset file pointer for StorageService
        await file.seek(0)