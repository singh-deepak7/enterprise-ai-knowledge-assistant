from fastapi import UploadFile

from app.ai.indexing.indexing_service import IndexingService
from app.core.logging import logger
from app.schemas.storage import StorageResult
from app.services.storage_service import StorageService
from app.services.validation_service import ValidationService


class DocumentService:
    """
    Handles the complete document upload workflow.
    """

    def __init__(
        self,
        validation_service: ValidationService,
        storage_service: StorageService,
        indexing_service: IndexingService | None = None,
    ) -> None:
        self.validation_service = validation_service
        self.storage_service = storage_service
        self.indexing_service = (
            indexing_service or IndexingService()
        )

    async def upload(
        self,
        file: UploadFile,
    ) -> StorageResult:
        """
        Validate, store, and index an uploaded document.
        """

        logger.info("Starting upload workflow")

        await self.validation_service.validate(file)

        result = await self.storage_service.save(file)

        logger.info(
            "Stored document '%s'. Starting indexing.",
            result.original_filename,
        )

        chunk_count = self.indexing_service.index_document(
            file_path=result.file_path,
            document_id=result.document_id,
            original_filename=result.original_filename,
        )

        logger.info(
            "Indexed %d chunk(s) for document %s.",
            chunk_count,
            result.document_id,
        )

        logger.info(
            "Upload workflow completed successfully."
        )

        return result