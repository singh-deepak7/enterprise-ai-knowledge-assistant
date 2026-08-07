from fastapi import APIRouter, Depends, status

from app.dependencies import get_document_repository
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import (
    DocumentListResponse,
    DocumentSummary,
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.get(
    "",
    response_model=DocumentListResponse,
    status_code=status.HTTP_200_OK,
)
def list_documents(
    repository: DocumentRepository = Depends(
        get_document_repository
    ),
) -> DocumentListResponse:
    """
    Return registered documents.
    """

    records = repository.list_all()

    documents = [
        DocumentSummary(
            document_id=record.document_id,
            original_filename=record.original_filename,
            content_type=record.content_type,
            size_bytes=record.size_bytes,
        )
        for record in records
    ]

    return DocumentListResponse(
        documents=documents,
    )