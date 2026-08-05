from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from app.ai.loaders.base_loader import BaseLoader
from app.core.logging import get_logger

logger = get_logger(__name__)


class PdfLoader(BaseLoader):
    """
    Loads PDF documents using LangChain's PyPDFLoader.
    """

    def load(self, file_path: Path) -> list[Document]:
        logger.info("Loading PDF document: %s", file_path.name)

        loader = PyPDFLoader(str(file_path))
        documents = loader.load()

        for index, document in enumerate(documents):
            document.metadata.update(
                {
                    "filename": file_path.name,
                    "extension": file_path.suffix.lower(),
                    "source": str(file_path),
                    "page_number": index + 1,
                }
            )

        logger.info(
            "Loaded %d pages from PDF '%s'",
            len(documents),
            file_path.name,
        )

        return documents