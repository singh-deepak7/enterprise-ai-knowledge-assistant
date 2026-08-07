from abc import ABC, abstractmethod

from langchain_core.documents import Document


class BaseVectorStoreProvider(ABC):
    """
    Abstract interface for vector store providers.
    """

    @abstractmethod
    def add_documents(
        self,
        documents: list[Document],
    ) -> None:
        """Index documents."""

    @abstractmethod
    def similarity_search(
        self,
        query: str,
        k: int = 5,
    ) -> list[Document]:
        """Retrieve similar documents."""

    @abstractmethod
    def similarity_search_with_scores(
        self,
        query: str,
        k: int = 5,
    ) -> list[tuple[Document, float]]:
        """
        Retrieve similar documents with relevance scores.

        Higher scores indicate greater relevance.
        """

    @abstractmethod
    def delete(
        self,
        ids: list[str],
    ) -> None:
        """Delete documents by id."""