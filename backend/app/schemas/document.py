from pydantic import BaseModel


class DocumentSummary(BaseModel):
    document_id: str
    original_filename: str
    content_type: str
    size_bytes: int


class DocumentListResponse(BaseModel):
    documents: list[DocumentSummary]