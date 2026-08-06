from app.services.document_service import DocumentService
from app.services.storage_service import StorageService
from app.services.validation_service import ValidationService
from app.ai.indexing.indexing_service import IndexingService


def get_storage_service() -> StorageService:
    return StorageService()


def get_validation_service() -> ValidationService:
    return ValidationService()

def get_indexing_service() -> IndexingService:
    return IndexingService()

def get_document_service() -> DocumentService:
    return DocumentService(
        validation_service=get_validation_service(),
        storage_service=get_storage_service(),
        indexing_service=get_indexing_service(),
    )