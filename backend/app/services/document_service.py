from fastapi import UploadFile

from app.ai.indexing.indexing_service import IndexingService
from app.core.logging import logger
from app.repositories.document_repository import (
    DocumentRecord,
    DocumentRepository,
)
from app.schemas.storage import StorageResult
from app.services.storage_service import StorageService
from app.services.validation_service import ValidationService

from pathlib import Path

from app.ai.vectorstores.vector_store_service import VectorStoreService


class DocumentService:
    """
    Handles the complete document upload workflow.
    """

    def __init__(
        self,
        validation_service: ValidationService,
        storage_service: StorageService,
        document_repository: DocumentRepository,
        vector_store_service: VectorStoreService,
        indexing_service: IndexingService | None = None,
    ) -> None:
        self.validation_service = validation_service
        self.storage_service = storage_service
        self.document_repository = document_repository
        self.vector_store_service = vector_store_service
        self.indexing_service = (
            indexing_service or IndexingService()
        )

    async def upload(
        self,
        file: UploadFile,
    ) -> StorageResult:
        """
        Validate, store, index, and register an uploaded document.
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

        self.document_repository.save(
            DocumentRecord(
                document_id=result.document_id,
                original_filename=result.original_filename,
                stored_filename=result.stored_filename,
                file_path=result.file_path,
                content_type=result.content_type,
                size_bytes=result.size_bytes,
            )
        )

        logger.info(
            "Registered document %s.",
            result.document_id,
        )

        logger.info(
            "Upload workflow completed successfully."
        )

        return result

    def delete(
        self,
        document_id: str,
    ) -> bool:
        """
        Delete a document from the vector store,
        filesystem, and document registry.

        Returns False when the document does not exist.
        """

        record = self.document_repository.get(
            document_id
        )

        if record is None:
            logger.warning(
                "Document %s not found for deletion.",
                document_id,
            )
            return False

        logger.info(
            "Starting deletion for document %s.",
            document_id,
        )

        # Delete indexed chunks first.
        self.vector_store_service.delete_by_document_id(
            document_id
        )

        # Delete the physical upload.
        file_path = Path(record.file_path)

        if file_path.exists():
            file_path.unlink()

            logger.info(
                "Deleted stored file for document %s.",
                document_id,
            )
        else:
            logger.warning(
                "Stored file not found for document %s: %s",
                document_id,
                record.file_path,
            )

        # Delete metadata last.
        self.document_repository.delete(
            document_id
        )

        logger.info(
            "Document %s deleted successfully.",
            document_id,
        )

        return True