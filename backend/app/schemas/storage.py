from pydantic import BaseModel


class StorageResult(BaseModel):
    document_id: str
    original_filename: str
    stored_filename: str
    file_path: str
    content_type: str
    size_bytes: int