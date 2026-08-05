import logging
import uuid

from langchain_core.documents import Document

from app.ai.chunking.text_splitter import create_text_splitter

logger = logging.getLogger(__name__)


class ChunkService:
    """
    Splits loaded documents into retrieval-ready chunks while enriching
    each chunk with metadata required by downstream AI services.
    """

    def __init__(self) -> None:
        self._splitter = create_text_splitter()

    def chunk_documents(
        self,
        documents: list[Document],
    ) -> list[Document]:
        """
        Split documents into chunks and enrich metadata.

        Args:
            documents: Source LangChain documents.

        Returns:
            List of chunked LangChain documents.
        """

        if not documents:
            logger.warning("No documents supplied for chunking.")
            return []

        chunks = self._splitter.split_documents(documents)

        total_chunks = len(chunks)

        if total_chunks == 0:
            logger.warning("Text splitter produced zero chunks.")
            return []

        chunk_sizes: list[int] = []

        for index, chunk in enumerate(chunks):
            size = len(chunk.page_content)
            chunk_sizes.append(size)

            chunk.metadata.update(
                {
                    "chunk_id": str(uuid.uuid4()),
                    "chunk_index": index,
                    "total_chunks": total_chunks,
                    "chunk_size": size,
                }
            )

        avg_size = sum(chunk_sizes) / total_chunks

        logger.info(
            (
                "Chunked %d document(s) into %d chunk(s). "
                "Avg size=%d chars | Min=%d | Max=%d"
            ),
            len(documents),
            total_chunks,
            int(avg_size),
            min(chunk_sizes),
            max(chunk_sizes),
        )

        return chunks