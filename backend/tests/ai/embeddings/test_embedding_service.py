from unittest.mock import Mock

from langchain_core.documents import Document

from app.ai.embeddings.embedding_service import EmbeddingService


def test_embed_documents():
    provider = Mock()

    provider.embed_documents.return_value = [
        [0.1, 0.2],
        [0.3, 0.4],
    ]

    service = EmbeddingService(provider)

    docs = [
        Document(page_content="Hello"),
        Document(page_content="World"),
    ]

    chunks, vectors = service.embed_documents(docs)

    assert chunks == docs
    assert len(vectors) == 2

    provider.embed_documents.assert_called_once_with(
        ["Hello", "World"]
    )


def test_empty_documents():
    provider = Mock()

    service = EmbeddingService(provider)

    chunks, vectors = service.embed_documents([])

    assert chunks == []
    assert vectors == []

    provider.embed_documents.assert_not_called()