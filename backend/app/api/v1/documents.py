from fastapi import APIRouter, status

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
)
def list_documents() -> dict[str, list[dict[str, object]]]:
    """
    Return indexed documents.

    This is a temporary empty response while the document
    repository/service layer is introduced in the next step.
    """

    return {
        "documents": [],
    }