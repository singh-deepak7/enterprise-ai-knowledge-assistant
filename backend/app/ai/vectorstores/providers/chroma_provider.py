import logging

from langchain_chroma import Chroma

from app.ai.embeddings.providers.base_embedding_provider import BaseEmbeddingProvider
from app.ai.embeddings.providers.openai_embedding_provider import OpenAIEmbeddingProvider
from app.ai.vectorstores.providers.base_provider import BaseVectorStoreProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class ChromaProvider(BaseVectorStoreProvider):
    """
    ChromaDB implementation of the vector store.
    """

    def __init__(
        self,
        embedding_provider: BaseEmbeddingProvider | None = None,
    ) -> None:

        self._embedding_provider = (
            embedding_provider or OpenAIEmbeddingProvider()
        )

        logger.info(
            "Initializing Chroma collection '%s'.",
            settings.CHROMA_COLLECTION,
        )

        self._store = Chroma(
            collection_name=settings.CHROMA_COLLECTION,
            persist_directory=settings.CHROMA_DB_DIR,
            embedding_function=self._embedding_provider.embedding_function,
        )

    def add_documents(
        self,
        documents,
    ) -> None:

        logger.info(
            "Adding %d document(s) to Chroma.",
            len(documents),
        )

        self._store.add_documents(documents)

    def similarity_search(
        self,
        query: str,
        k: int = 5,
    ):

        logger.info(
            "Searching Chroma (top_k=%d).",
            k,
        )

        return self._store.similarity_search(
            query=query,
            k=k,
        )

    def delete(
        self,
        ids: list[str],
    ) -> None:

        logger.info(
            "Deleting %d document(s).",
            len(ids),
        )

        self._store.delete(ids=ids)