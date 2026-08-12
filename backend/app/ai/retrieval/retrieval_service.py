import logging

from langchain_core.documents import Document

from app.ai.vectorstores.vector_store_service import VectorStoreService
from app.core.config import settings

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
        Retrieve relevant chunks for a query.

        Results below the configured relevance threshold
        are excluded.
        """

        logger.info(
            "Retrieving documents for query "
            "(top_k=%d threshold=%.2f).",
            top_k,
            settings.SIMILARITY_SCORE_THRESHOLD,
        )

        results = (
            self._vector_store.similarity_search_with_scores(
                query=query,
                k=top_k,
            )
        )

        documents: list[Document] = []

        for document, score in results:
            logger.info(
                "Retrieved chunk relevance_score=%.4f "
                "source=%s page=%s",
                score,
                document.metadata.get(
                    "original_filename",
                    document.metadata.get(
                        "source",
                        "Unknown",
                    ),
                ),
                document.metadata.get("page"),
            )

            if (
                score
                >= settings.SIMILARITY_SCORE_THRESHOLD
            ):
                # Preserve the retrieval score so later
                # workflow stages can use it if needed.
                document.metadata[
                    "relevance_score"
                ] = score

                documents.append(document)

        logger.info(
            "Retrieved %d candidate(s); "
            "%d passed relevance threshold %.2f.",
            len(results),
            len(documents),
            settings.SIMILARITY_SCORE_THRESHOLD,
        )

        return documents