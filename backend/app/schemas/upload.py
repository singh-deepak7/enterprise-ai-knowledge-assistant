from pydantic import BaseModel

from app.schemas.storage import StorageResult


class UploadResponse(BaseModel):
    success: bool
    message: str
    data: StorageResult