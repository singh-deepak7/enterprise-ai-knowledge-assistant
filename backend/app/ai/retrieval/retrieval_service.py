import logging

from langchain_core.documents import Document

from app.ai.vectorstores.vector_store_service import VectorStoreService

logger = logging.getLogger(__name__)


class RetrievalService:
    """
    Service responsible for retrieving relevant document chunks.
    """

    def __init__(
        self,
        vector_store_service: VectorStoreService | None = None,
    ) -> None:
        self._vector_store = (
            vector_store_service or VectorStoreService()
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[Document]:
        """
        Retrieve the most relevant chunks for a query.
        """

        logger.info(
            "Retrieving documents for query (top_k=%d).",
            top_k,
        )

        documents = self._vector_store.similarity_search(
            query=query,
            k=top_k,
        )

        logger.info(
            "Retrieved %d document(s).",
            len(documents),
        )

        return documents