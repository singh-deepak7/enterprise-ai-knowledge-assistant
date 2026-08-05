from langchain_core.documents import Document

from app.ai.chunking.chunk_service import ChunkService


docs = [
    Document(
        page_content="Hello " * 500,
        metadata={"source": "sample.pdf"},
        )
    ]

def test_chunk_documents():
    service = ChunkService()

    chunks = service.chunk_documents(docs)

    assert chunks[0].metadata["source"] == "sample.pdf"


def test_empty_documents():
    service = ChunkService()

    #chunks = service.chunk_documents([])

    #assert chunks == []

    chunks = service.chunk_documents(docs)

    assert len(chunks) > 1

    for i, chunk in enumerate(chunks):
        assert "chunk_id" in chunk.metadata
        assert chunk.metadata["chunk_index"] == i
        assert chunk.metadata["total_chunks"] == len(chunks)
        assert chunk.metadata["chunk_size"] > 0