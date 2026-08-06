import logging

from langchain_core.documents import Document

from app.ai.llm.llm_service import LLMService
from app.ai.llm.prompt_builder import PromptBuilder
from app.ai.retrieval.retrieval_service import RetrievalService
from app.ai.retrieval.source_attribution import (
    SourceAttribution,
)

logger = logging.getLogger(__name__)


class RAGService:
    """
    Service responsible for orchestrating the Retrieval-Augmented
    Generation (RAG) workflow.
    """

    def __init__(
    self,
    retrieval_service: RetrievalService | None = None,
    prompt_builder: PromptBuilder | None = None,
    llm_service: LLMService | None = None,
    source_attribution: SourceAttribution | None = None,
    ) -> None:
        self._retrieval_service = (
            retrieval_service or RetrievalService()
        )

        self._prompt_builder = (
            prompt_builder or PromptBuilder()
        )

        self._llm_service = (
            llm_service or LLMService()
        )

        self._source_attribution = (
            source_attribution or SourceAttribution()
        )

    def generate_answer(
        self,
        question: str,
        top_k: int = 5,
    ) -> dict[str, str | list[Document]]:
        """
        Execute the complete Retrieval-Augmented Generation workflow.

        Args:
            question: User question.
            top_k: Number of relevant documents to retrieve.

        Returns:
            Dictionary containing the generated answer and
            retrieved source documents.
        """

        logger.info(
            "Starting RAG pipeline (top_k=%d).",
            top_k,
        )

        try:
            documents = self._retrieval_service.retrieve(
                query=question,
                top_k=top_k,
            )

            logger.info(
                "Retrieved %d document(s).",
                len(documents),
            )

            prompt = self._prompt_builder.build_prompt(
                question=question,
                documents=documents,
            )

            logger.info("Prompt successfully built.")

            answer = self._llm_service.generate(
                prompt=prompt,
            )

            logger.info("RAG pipeline completed successfully.")

            sources = self._source_attribution.build_sources(
                documents,
            )

            return {
                "answer": answer,
                "sources": sources,
            }

        except Exception:
            logger.exception(
                "Error while executing RAG pipeline."
            )
            raise