import logging
from pathlib import Path

from app.ai.chunking.chunk_service import ChunkService
from app.ai.loaders.loader_factory import LoaderFactory
from app.ai.vectorstores.vector_store_service import VectorStoreService

logger = logging.getLogger(__name__)


class IndexingService:
    """
    Coordinates the document indexing workflow.
    """

    def __init__(
        self,
        chunk_service: ChunkService | None = None,
        vector_store_service: VectorStoreService | None = None,
    ) -> None:
        self._chunk_service = chunk_service or ChunkService()
        self._vector_store_service = (
            vector_store_service or VectorStoreService()
        )

    def index_document(
        self,
        file_path: str | Path,
        document_id: str | None = None,
        original_filename: str | None = None,
    ) -> int:
        """
        Load, enrich, chunk, and index a document.

        Args:
            file_path:
                Path to the stored document.
            document_id:
                Unique identifier assigned during storage.
            original_filename:
                Human-readable filename supplied by the user.

        Returns:
            Number of chunks indexed.
        """

        file_path = Path(file_path)

        logger.info(
            "Starting indexing for %s",
            file_path.name,
        )

        loader = LoaderFactory.get_loader(
            file_path,
        )

        documents = loader.load(
            file_path,
        )

        logger.info(
            "Loaded %d document(s)",
            len(documents),
        )

        # Add storage-level metadata before chunking.
        #
        # The loader sees the UUID-based stored filename,
        # while original_filename preserves the filename
        # uploaded by the user.
        for document in documents:
            if document_id:
                document.metadata[
                    "document_id"
                ] = document_id

            if original_filename:
                document.metadata[
                    "original_filename"
                ] = original_filename

            document.metadata[
                "stored_filename"
            ] = file_path.name

        chunks = (
            self._chunk_service.chunk_documents(
                documents,
            )
        )

        logger.info(
            "Generated %d chunk(s)",
            len(chunks),
        )

        self._vector_store_service.add_documents(
            chunks,
        )

        logger.info(
            "Successfully indexed '%s' with %d chunk(s)",
            original_filename or file_path.name,
            len(chunks),
        )

        return len(chunks)