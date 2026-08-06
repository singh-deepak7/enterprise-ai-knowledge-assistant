import logging

from langchain_core.documents import Document

from app.ai.vectorstores.providers.base_provider import (
    BaseVectorStoreProvider,
)
from app.ai.vectorstores.providers.chroma_provider import ChromaProvider

logger = logging.getLogger(__name__)


class VectorStoreService:
    """
    High-level service for vector store operations.
    """

    def __init__(
        self,
        provider: BaseVectorStoreProvider | None = None,
    ) -> None:
        self._provider = provider or ChromaProvider()

    def add_documents(
        self,
        documents: list[Document],
    ) -> None:
        """
        Add documents to the vector store.
        """

        if not documents:
            logger.warning("No documents supplied for indexing.")
            return

        logger.info(
            "Indexing %d document(s).",
            len(documents),
        )

        self._provider.add_documents(documents)

    def similarity_search(
        self,
        query: str,
        k: int = 5,
    ) -> list[Document]:
        """
        Search for similar documents.
        """

        logger.info(
            "Executing similarity search (top_k=%d).",
            k,
        )

        return self._provider.similarity_search(
            query=query,
            k=k,
        )

    def delete(
        self,
        ids: list[str],
    ) -> None:
        """
        Delete indexed documents.
        """

        if not ids:
            logger.warning("No document ids supplied for deletion.")
            return

        self._provider.delete(ids)