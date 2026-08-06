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

        Args:
            documents: Retrieved LangChain documents.

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

            sources.append(
                {
                    "source": metadata.get(
                        "source",
                        "Unknown",
                    ),
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