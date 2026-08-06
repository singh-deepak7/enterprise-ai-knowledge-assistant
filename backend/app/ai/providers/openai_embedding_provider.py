import logging

from langchain_openai import OpenAIEmbeddings

from app.ai.providers.base_embedding_provider import BaseEmbeddingProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """
    OpenAI implementation of the embedding provider.
    """

    def __init__(self) -> None:
        logger.info(
            "Initializing OpenAI embedding provider with model '%s'.",
            settings.OPENAI_EMBEDDING_MODEL,
        )

        self._embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
        )

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple documents.
        """

        logger.info(
            "Generating embeddings for %d document(s).",
            len(texts),
        )

        return self._embeddings.embed_documents(texts)

    def embed_query(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate an embedding for a search query.
        """

        logger.debug("Generating query embedding.")

        return self._embeddings.embed_query(text)