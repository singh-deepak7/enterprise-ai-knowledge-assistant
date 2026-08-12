from __future__ import annotations

from unittest.mock import Mock

import pytest
from langchain_core.documents import Document

from app.ai.agentic.graph_state import GraphState
from app.ai.agentic.nodes.reasoning_node import reasoning_node
from app.ai.llm.llm_service import (
    LLMResponse,
    LLMService,
)
from app.ai.llm.prompt_builder import PromptBuilder


def _mock_llm_response(answer: str = "ANSWER") -> LLMResponse:
    return LLMResponse(
        answer=answer,
        provider="OpenAI",
        model="gpt-4.1-mini",
        prompt_tokens=120,
        completion_tokens=35,
        total_tokens=155,
        finish_reason="stop",
        latency_ms=215.7,
        retry_count=0,
    )


def test_reasoning_node_success() -> None:
    """
    The reasoning node should build the prompt, invoke the LLM,
    and populate the graph state.
    """

    documents = [
        Document(
            page_content="Comprehensive coverage protects against theft.",
            metadata={
                "source": "policy.pdf",
                "page": 2,
            },
        )
    ]

    prompt_builder = Mock(spec=PromptBuilder)
    prompt_builder.build_prompt.return_value = "PROMPT"

    llm_service = Mock(spec=LLMService)
    llm_service.generate.return_value = _mock_llm_response(
        "Comprehensive coverage protects against theft."
    )

    state = GraphState(
        question="What is comprehensive coverage?",
        retrieved_chunks=documents,
    )

    result = reasoning_node(
        state=state,
        prompt_builder=prompt_builder,
        llm_service=llm_service,
    )

    prompt_builder.build_prompt.assert_called_once_with(
        question="What is comprehensive coverage?",
        documents=documents,
        conversation_history=[],
    )

    llm_service.generate.assert_called_once_with(
        prompt="PROMPT",
    )

    assert result is state
    assert result.prompt == "PROMPT"

    assert (
        result.answer
        == "Comprehensive coverage protects against theft."
    )

    assert "reasoning" in result.metadata

    metadata = result.metadata["reasoning"]

    assert metadata["duration_ms"] >= 0
    assert metadata["prompt_length"] == len("PROMPT")
    assert metadata["answer_length"] == len(
        "Comprehensive coverage protects against theft."
    )

    assert metadata["provider"] == "OpenAI"
    assert metadata["model"] == "gpt-4.1-mini"
    assert metadata["prompt_tokens"] == 120
    assert metadata["completion_tokens"] == 35
    assert metadata["total_tokens"] == 155
    assert metadata["finish_reason"] == "stop"
    assert metadata["llm_latency_ms"] == 215.7


def test_reasoning_node_preserves_retrieved_chunks() -> None:
    """
    Retrieved documents should remain unchanged.
    """

    documents = [
        Document(
            page_content="Coverage",
            metadata={},
        )
    ]

    prompt_builder = Mock(spec=PromptBuilder)
    prompt_builder.build_prompt.return_value = "PROMPT"

    llm_service = Mock(spec=LLMService)
    llm_service.generate.return_value = _mock_llm_response()

    state = GraphState(
        question="Coverage?",
        retrieved_chunks=documents,
    )

    reasoning_node(
        state=state,
        prompt_builder=prompt_builder,
        llm_service=llm_service,
    )

    assert state.retrieved_chunks == documents


def test_reasoning_node_preserves_existing_metadata() -> None:
    """
    Existing metadata should not be overwritten.
    """

    prompt_builder = Mock(spec=PromptBuilder)
    prompt_builder.build_prompt.return_value = "PROMPT"

    llm_service = Mock(spec=LLMService)
    llm_service.generate.return_value = _mock_llm_response()

    state = GraphState(
        question="Coverage",
        metadata={
            "planner": {
                "workflow": "rag",
            },
            "retrieval": {
                "chunk_count": 3,
            },
        },
    )

    reasoning_node(
        state=state,
        prompt_builder=prompt_builder,
        llm_service=llm_service,
    )

    assert state.metadata["planner"]["workflow"] == "rag"

    assert state.metadata["retrieval"]["chunk_count"] == 3

    assert "reasoning" in state.metadata


def test_reasoning_node_propagates_prompt_builder_exception() -> None:
    """
    Prompt builder failures should propagate.
    """

    prompt_builder = Mock(spec=PromptBuilder)

    prompt_builder.build_prompt.side_effect = RuntimeError(
        "Prompt builder failed"
    )

    llm_service = Mock(spec=LLMService)

    state = GraphState(
        question="Coverage",
    )

    with pytest.raises(RuntimeError):
        reasoning_node(
            state=state,
            prompt_builder=prompt_builder,
            llm_service=llm_service,
        )


def test_reasoning_node_propagates_llm_exception() -> None:
    """
    LLM failures should propagate.
    """

    prompt_builder = Mock(spec=PromptBuilder)
    prompt_builder.build_prompt.return_value = "PROMPT"

    llm_service = Mock(spec=LLMService)

    llm_service.generate.side_effect = RuntimeError(
        "OpenAI unavailable"
    )

    state = GraphState(
        question="Coverage",
    )

    with pytest.raises(RuntimeError):
        reasoning_node(
            state=state,
            prompt_builder=prompt_builder,
            llm_service=llm_service,
        )


def test_reasoning_node_preserves_question() -> None:
    """
    The original user question should remain unchanged.
    """

    prompt_builder = Mock(spec=PromptBuilder)
    prompt_builder.build_prompt.return_value = "PROMPT"

    llm_service = Mock(spec=LLMService)
    llm_service.generate.return_value = _mock_llm_response()

    state = GraphState(
        question="What is liability insurance?",
    )

    reasoning_node(
        state=state,
        prompt_builder=prompt_builder,
        llm_service=llm_service,
    )

    assert state.question == "What is liability insurance?"