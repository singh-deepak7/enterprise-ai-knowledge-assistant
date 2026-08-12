import logging

from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class SourceAttribution:
    """
    Builds API-friendly source attribution information
    from retrieved LangChain documents.
    """

    def build_sources(
        self,
        documents: list[Document],
    ) -> list[dict]:
        """
        Convert retrieved documents into source metadata.

        Prefer the original uploaded filename for user-facing
        citations while falling back to the stored source path
        for documents indexed before original filename metadata
        was introduced.

        Args:
            documents:
                Retrieved LangChain documents.

        Returns:
            List of source metadata dictionaries.
        """

        logger.info(
            "Building source attribution for %d document(s).",
            len(documents),
        )

        sources: list[dict] = []

        for document in documents:
            metadata = document.metadata or {}

            source = (
                metadata.get("original_filename")
                or metadata.get("source")
                or "Unknown"
            )

            sources.append(
                {
                    "source": source,
                    "page": metadata.get(
                        "page",
                    ),
                    "chunk": metadata.get(
                        "chunk",
                    ),
                }
            )

        logger.info(
            "Built %d source attribution entries.",
            len(sources),
        )

        return sources