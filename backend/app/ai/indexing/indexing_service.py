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
    ) -> int:
        """
        Load, chunk, and index a document.

        Args:
            file_path: Path to the document.

        Returns:
            Number of chunks indexed.
        """

        file_path = Path(file_path)

        logger.info("Starting indexing for %s", file_path.name)

        # Select appropriate loader
        loader = LoaderFactory.get_loader(file_path)

        # Load document
        documents = loader.load(file_path)

        logger.info("Loaded %d document(s)", len(documents))

        # Chunk document
        chunks = self._chunk_service.chunk_documents(documents)

        logger.info("Generated %d chunk(s)", len(chunks))

        # Store in vector database
        self._vector_store_service.add_documents(chunks)

        logger.info(
            "Successfully indexed '%s' with %d chunk(s)",
            file_path.name,
            len(chunks),
        )

        return len(chunks)