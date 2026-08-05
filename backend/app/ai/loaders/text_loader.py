from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document

from app.ai.loaders.base_loader import BaseLoader
from app.core.logging import get_logger

logger = get_logger(__name__)


class TxtLoader(BaseLoader):
    """
    Loads plain text files into LangChain Document objects.
    """

    def load(self, file_path: Path) -> list[Document]:
        logger.info("Loading text document: %s", file_path.name)

        loader = TextLoader(str(file_path), encoding="utf-8")
        documents = loader.load()

        for document in documents:
            document.metadata.update(
                {
                    "filename": file_path.name,
                    "extension": file_path.suffix.lower(),
                    "source": str(file_path),
                }
            )

        logger.info(
            "Loaded text document '%s'",
            file_path.name,
        )

        return documents