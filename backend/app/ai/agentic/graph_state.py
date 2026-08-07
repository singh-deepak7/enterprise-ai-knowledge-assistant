"""
Shared graph state passed between LangGraph nodes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from langchain_core.documents import Document

from app.ai.memory.conversation_memory import ConversationTurn


@dataclass(slots=True)
class GraphState:
    """
    Shared mutable state for the agentic workflow.

    Each node enriches this object instead of creating
    new response objects.
    """

    # ==========================================================
    # User Request
    # ==========================================================

    question: str

    # Unique request identifier for end-to-end tracing.
    request_id: str = ""

    # ==========================================================
    # Planner Output
    # ==========================================================

    intent: str = "general_qa"

    retrieval_strategy: str = "hybrid"

    top_k: int = 5

    requires_retrieval: bool = True

    # ==========================================================
    # Retrieval Output
    # ==========================================================

    retrieved_chunks: list[Document] = field(default_factory=list)

    # ==========================================================
    # Reasoning Output
    # ==========================================================

    prompt: str = ""

    answer: str = ""

    # ==========================================================
    # Validation Output
    # ==========================================================

    validated: bool = False

    # Will be enhanced in Sprint 9.4
    confidence_score: float = 0.0

    # ==========================================================
    # Response Metadata
    # ==========================================================

    sources: list[dict[str, object]] = field(default_factory=list)

    metadata: dict[str, object] = field(default_factory=dict)

    # ==========================================================
    # Conversation History
    # ==========================================================

    conversation_history: list[ConversationTurn] = field(
        default_factory=list
    )