from unittest.mock import Mock

from langchain_core.documents import Document

from app.ai.vectorstores.vector_store_service import VectorStoreService


def test_add_documents_success():
    """
    Verify documents are delegated to the provider.
    """
    provider = Mock()

    service = VectorStoreService(provider)

    docs = [
        Document(page_content="Document 1"),
        Document(page_content="Document 2"),
    ]

    service.add_documents(docs)

    provider.add_documents.assert_called_once_with(docs)


def test_add_documents_empty():
    """
    Verify no provider call is made for an empty list.
    """
    provider = Mock()

    service = VectorStoreService(provider)

    service.add_documents([])

    provider.add_documents.assert_not_called()


def test_similarity_search():
    """
    Verify similarity search is delegated correctly.
    """
    provider = Mock()

    expected = [
        Document(page_content="Result 1"),
        Document(page_content="Result 2"),
    ]

    provider.similarity_search.return_value = expected

    service = VectorStoreService(provider)

    results = service.similarity_search(
        query="insurance claim",
        k=2,
    )

    assert results == expected

    provider.similarity_search.assert_called_once_with(
        query="insurance claim",
        k=2,
    )


def test_similarity_search_default_k():
    """
    Verify default top-k value.
    """
    provider = Mock()

    provider.similarity_search.return_value = []

    service = VectorStoreService(provider)

    service.similarity_search("policy")

    provider.similarity_search.assert_called_once_with(
        query="policy",
        k=5,
    )


def test_delete_documents():
    """
    Verify delete delegates ids.
    """
    provider = Mock()

    service = VectorStoreService(provider)

    ids = [
        "id-1",
        "id-2",
    ]

    service.delete(ids)

    provider.delete.assert_called_once_with(ids)


def test_delete_empty():
    """
    Verify delete is skipped for an empty id list.
    """
    provider = Mock()

    service = VectorStoreService(provider)

    service.delete([])

    provider.delete.assert_not_called()