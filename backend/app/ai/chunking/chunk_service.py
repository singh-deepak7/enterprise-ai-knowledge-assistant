import logging

from langchain_core.documents import Document

from app.ai.chunking.text_splitter import create_text_splitter

logger = logging.getLogger(__name__)


class ChunkService:
    """
    Splits loaded documents into retrieval-ready chunks.
    """

    def __init__(self):
        self.splitter = create_text_splitter()

    def chunk_documents(
        self,
        documents: list[Document],
    ) -> list[Document]:
        """
        Split documents into chunks while preserving metadata.
        """

        if not documents:
            logger.warning("No documents supplied for chunking.")
            return []

        chunks = self.splitter.split_documents(documents)

        logger.info(
            "Chunked %d documents into %d chunks.",
            len(documents),
            len(chunks),
        )

        return chunks