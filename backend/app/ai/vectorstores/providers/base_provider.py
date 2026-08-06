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
    def delete(
        self,
        ids: list[str],
    ) -> None:
        """Delete documents by id."""