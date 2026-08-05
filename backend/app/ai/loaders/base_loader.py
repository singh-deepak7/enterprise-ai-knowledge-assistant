from abc import ABC, abstractmethod
from pathlib import Path

from langchain_core.documents import Document


class BaseLoader(ABC):
    """
    Abstract base class for all document loaders.

    Every loader must convert a supported file into a list of
    LangChain Document objects.
    """

    @abstractmethod
    def load(self, file_path: Path) -> list[Document]:
        """
        Load a file and return LangChain documents.

        Args:
            file_path: Path to the source file.

        Returns:
            List of LangChain Document objects.
        """
        pass