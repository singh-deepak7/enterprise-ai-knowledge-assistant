from pydantic import BaseModel


class DocumentSummary(BaseModel):
    document_id: str
    original_filename: str
    content_type: str
    size_bytes: int
    uploaded_at: str
    chunk_count: int
    status: str


class DocumentListResponse(BaseModel):
    documents: list[DocumentSummary]