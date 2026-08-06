"""
Shared graph state passed between LangGraph nodes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from langchain_core.documents import Document


@dataclass
class GraphState:
    """
    Shared workflow state for the LangGraph pipeline.
    """

    # Original user query
    question: str

    # Retrieved context documents
    retrieved_chunks: list[Document] = field(default_factory=list)

    # Prompt generated for the LLM
    prompt: str = ""

    # LLM response
    answer: str = ""

    # Final source attribution
    sources: list[dict[str, object]] = field(default_factory=list)

    # Workflow metadata
    metadata: dict[str, object] = field(default_factory=dict)