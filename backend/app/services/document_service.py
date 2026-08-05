from fastapi import UploadFile

from app.core.logging import logger
from app.schemas.storage import StorageResult
from app.services.storage_service import StorageService
from app.services.validation_service import ValidationService


class DocumentService:
    """
    Handles the document upload workflow.
    """

    def __init__(
        self,
        validation_service: ValidationService,
        storage_service: StorageService,
    ) -> None:
        self.validation_service = validation_service
        self.storage_service = storage_service

    async def upload(self, file: UploadFile) -> StorageResult:
        """
        Validate and store an uploaded document.
        """

        logger.info("Starting upload workflow")

        await self.validation_service.validate(file)

        result = await self.storage_service.save(file)

        logger.info(
            "Upload completed successfully. Document ID=%s",
            result.document_id,
        )

        return result