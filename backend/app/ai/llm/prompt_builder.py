import logging

from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    Builds prompts for Retrieval-Augmented Generation (RAG).

    This class formats retrieved document chunks into a grounded prompt
    that instructs the LLM to answer using only the supplied context.
    """

    def build_prompt(
        self,
        question: str,
        documents: list[Document],
    ) -> str:
        """
        Build a RAG prompt from the user question and retrieved documents.

        Args:
            question: User's question.
            documents: Retrieved document chunks.

        Returns:
            Formatted prompt string.
        """

        logger.info(
            "Building prompt using %d retrieved document(s).",
            len(documents),
        )

        context_sections: list[str] = []

        for index, document in enumerate(documents, start=1):
            metadata = document.metadata or {}

            source = metadata.get("source", "Unknown")
            page = metadata.get("page", "N/A")

            context_sections.append(
                (
                    f"[Document {index}]\n"
                    f"Source: {source}\n"
                    f"Page: {page}\n\n"
                    f"{document.page_content}"
                )
            )

        context = "\n\n------------------------------\n\n".join(
            context_sections
        )

        prompt = f"""You are an Enterprise AI Knowledge & Decision Support Assistant.

Your responsibilities:
- Answer ONLY using the supplied context.
- Do NOT make up information.
- If the answer is not contained in the context, say:
  "I couldn't find that information in the provided documents."
- Be concise, accurate, and professional.

Context
------------------------------
{context}
------------------------------

Question:
{question}

Answer:
"""

        logger.debug("Prompt built successfully.")

        return prompt.strip()