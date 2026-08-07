from fastapi import APIRouter, status

from app.schemas.document import DocumentListResponse

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.get(
    "",
    response_model=DocumentListResponse,
    status_code=status.HTTP_200_OK,
)
def list_documents() -> DocumentListResponse:
    """
    Return indexed documents.
    """

    return DocumentListResponse(
        documents=[],
    )