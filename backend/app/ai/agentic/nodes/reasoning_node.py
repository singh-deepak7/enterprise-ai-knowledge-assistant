"""
LangGraph Reasoning Node.

This node builds the grounded RAG prompt and invokes the LLM using
the existing PromptBuilder and LLMService.
"""

from __future__ import annotations

import logging
import time

from app.ai.agentic.graph_state import GraphState
from app.ai.llm.llm_service import LLMService
from app.ai.llm.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)


def reasoning_node(
    state: GraphState,
    prompt_builder: PromptBuilder,
    llm_service: LLMService,
) -> GraphState:
    """
    Build the prompt, invoke the LLM, and update the graph state.

    Args:
        state:
            Current workflow state.

        prompt_builder:
            Existing PromptBuilder.

        llm_service:
            Existing LLMService.

    Returns:
        Updated GraphState.
    """

    logger.info("Reasoning node started.")

    start = time.perf_counter()

    try:
        logger.debug(
            "Building prompt using %d retrieved document(s).",
            len(state.retrieved_chunks),
        )

        prompt = prompt_builder.build_prompt(
            question=state.question,
            documents=state.retrieved_chunks,
            conversation_history=state.conversation_history,
        )

        state.prompt = prompt

        logger.debug("Prompt successfully built.")

        answer = llm_service.generate(
            prompt=prompt,
        )

        state.answer = answer

        elapsed_ms = round(
            (time.perf_counter() - start) * 1000,
            2,
        )

        state.metadata["reasoning"] = {
            "duration_ms": elapsed_ms,
            "prompt_length": len(prompt),
            "answer_length": len(answer),
        }

        logger.info("Reasoning node completed.")

        return state

    except Exception:
        logger.exception(
            "Reasoning node failed."
        )
        raise