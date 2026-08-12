import logging

from langchain_core.documents import Document

from app.ai.memory.conversation_memory import ConversationTurn

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    Builds prompts for Retrieval-Augmented Generation (RAG).

    This class formats retrieved document chunks and optional
    conversation history into a grounded prompt that instructs
    the LLM to answer using only the supplied context.
    """

    def _format_conversation(
        self,
        history: list[ConversationTurn],
    ) -> str:
        """
        Format conversation history into a readable transcript.
        """
        if not history:
            return ""

        lines: list[str] = []

        for turn in history:
            role = "User" if turn.role == "user" else "Assistant"
            lines.append(f"{role}: {turn.content}")

        return "\n".join(lines)

    def build_prompt(
        self,
        question: str,
        documents: list[Document],
        conversation_history: list[ConversationTurn] | None = None,
    ) -> str:
        """
        Build a RAG prompt from the user question, retrieved documents,
        and optional conversation history.

        Args:
            question: User's current question.
            documents: Retrieved document chunks.
            conversation_history: Previous conversation turns.

        Returns:
            Fully formatted prompt.
        """

        logger.info(
            "Building prompt using %d retrieved document(s).",
            len(documents),
        )

        # ------------------------------------------------------------------
        # Conversation History
        # ------------------------------------------------------------------

        conversation_section = ""

        if conversation_history:
            conversation_section = (
                "## Conversation History\n\n"
                f"{self._format_conversation(conversation_history)}\n\n"
            )

        # ------------------------------------------------------------------
        # Retrieved Context
        # ------------------------------------------------------------------

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

        if not context:
            context = "No relevant documents were retrieved."

        # ------------------------------------------------------------------
        # Final Prompt
        # ------------------------------------------------------------------

        prompt = f"""You are an Enterprise AI Knowledge & Decision Support Assistant.

Your responsibilities:

- Answer ONLY using the supplied context.
- Use the conversation history only to understand follow-up questions.
- Do NOT introduce facts that are not present in the retrieved context.
- Do NOT make up information.
- If the answer cannot be found in the supplied context, reply exactly:
  "I couldn't find that information in the provided documents."
- Be concise, accurate, and professional.

{conversation_section}## Retrieved Context

{context}

## Current Question

{question}

## Answer
"""

        logger.debug("Prompt built successfully.")

        return prompt.strip()