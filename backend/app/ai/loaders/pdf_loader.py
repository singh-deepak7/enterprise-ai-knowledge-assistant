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
            metadata = self.build_base_metadata(file_path)
            metadata["page_number"] = index + 1

            document.metadata.update(metadata)

        logger.info(
            "Loaded %d pages from PDF '%s'",
            len(documents),
            file_path.name,
        )

        return documents