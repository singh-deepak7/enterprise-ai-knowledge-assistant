import logging

from langchain_core.documents import Document

from app.ai.providers.base_embedding_provider import BaseEmbeddingProvider
from app.ai.providers.openai_embedding_provider import (
    OpenAIEmbeddingProvider,
)

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Generates embeddings for document chunks.
    """

    def __init__(
        self,
        provider: BaseEmbeddingProvider | None = None,
    ) -> None:
        self._provider = provider or OpenAIEmbeddingProvider()

    def embed_documents(
        self,
        chunks: list[Document],
    ) -> tuple[list[Document], list[list[float]]]:
        """
        Generate embeddings for a collection of chunks.

        Returns:
            Original chunks and corresponding embedding vectors.
        """

        if not chunks:
            logger.warning("No chunks supplied for embedding.")
            return [], []

        texts = [chunk.page_content for chunk in chunks]

        vectors = self._provider.embed_documents(texts)

        logger.info(
            "Generated %d embedding vector(s).",
            len(vectors),
        )

        return chunks, vectors

    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        """
        Generate an embedding for a search query.
        """

        return self._provider.embed_query(query)