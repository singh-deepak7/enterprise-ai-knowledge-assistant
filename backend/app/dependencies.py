from functools import lru_cache

from app.ai.agentic.workflow import AgenticWorkflow
from app.ai.indexing.indexing_service import IndexingService
from app.repositories.document_repository import DocumentRepository
from app.services.document_service import DocumentService
from app.services.storage_service import StorageService
from app.services.validation_service import ValidationService


def get_storage_service() -> StorageService:
    return StorageService()


def get_validation_service() -> ValidationService:
    return ValidationService()


def get_indexing_service() -> IndexingService:
    return IndexingService()


@lru_cache
def get_document_repository() -> DocumentRepository:
    """
    Returns the shared in-memory document repository.
    """

    return DocumentRepository()


def get_document_service() -> DocumentService:
    return DocumentService(
        validation_service=get_validation_service(),
        storage_service=get_storage_service(),
        indexing_service=get_indexing_service(),
        document_repository=get_document_repository(),
    )


@lru_cache
def get_agentic_workflow() -> AgenticWorkflow:
    """
    Returns a singleton AgenticWorkflow.

    The LangGraph is compiled only once and reused
    across all requests.
    """

    return AgenticWorkflow()