from fastapi import APIRouter, Depends, File, UploadFile, status

from app.dependencies import get_document_service
from app.schemas.upload import UploadResponse
from app.services.document_service import DocumentService

router = APIRouter()


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    document_service: DocumentService = Depends(get_document_service),
):
    result = await document_service.upload(file)

    return UploadResponse(
        success=True,
        message="Document uploaded successfully.",
        data=result,
    )