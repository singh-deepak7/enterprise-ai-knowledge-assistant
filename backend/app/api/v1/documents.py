from fastapi import APIRouter, Depends, status

from app.dependencies import get_document_repository
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import (
    DocumentListResponse,
    DocumentSummary,
)
from app.services.document_service import DocumentService
from app.dependencies import (
    get_document_repository,
    get_document_service,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
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
            uploaded_at=record.uploaded_at,
            chunk_count=record.chunk_count,
            status=record.status,
        )
        for record in records
    ]

    return DocumentListResponse(
        documents=documents,
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: str,
    service: DocumentService = Depends(
        get_document_service
    ),
) -> None:
    """
    Delete a document and all associated data.
    """

    deleted = service.delete(
        document_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )