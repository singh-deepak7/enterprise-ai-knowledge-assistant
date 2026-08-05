from abc import ABC, abstractmethod
from pathlib import Path

from langchain_core.documents import Document


class BaseLoader(ABC):
    """
    Abstract base class for all document loaders.
    """

    @abstractmethod
    def load(self, file_path: Path) -> list[Document]:
        """
        Load a file and return LangChain documents.
        """
        pass

    def build_base_metadata(self, file_path: Path) -> dict[str, str]:
        """
        Build common metadata shared by all document types.
        """
        return {
            "filename": file_path.name,
            "extension": file_path.suffix.lower(),
            "source": str(file_path),
        }