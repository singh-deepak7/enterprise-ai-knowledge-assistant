from langchain_core.documents import Document

from app.ai.chunking.chunk_service import ChunkService


def test_chunk_documents():
    service = ChunkService()

    docs = [
        Document(page_content="Hello world " * 500)
    ]

    chunks = service.chunk_documents(docs)

    assert len(chunks) > 1


def test_empty_documents():
    service = ChunkService()

    chunks = service.chunk_documents([])

    assert chunks == []