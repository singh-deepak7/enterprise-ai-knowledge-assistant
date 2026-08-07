from unittest.mock import Mock

from langchain_core.documents import Document

from app.ai.agentic.workflow import AgenticWorkflow
from app.ai.llm.llm_service import LLMResponse


def test_agentic_workflow_smoke() -> None:
    """
    Smoke test for the complete LangGraph workflow.

    Verifies that all nodes execute together using mocked
    dependencies without calling external services.
    """

    retrieval_service = Mock()

    retrieval_service.retrieve.return_value = [
        Document(
            page_content=(
                "Comprehensive coverage pays for damage "
                "caused by theft, fire and hail."
            ),
            metadata={
                "source": "policy.pdf",
                "page": 2,
                "chunk": 5,
            },
        )
    ]

    prompt_builder = Mock()

    prompt_builder.build_prompt.return_value = (
        "Mock Prompt"
    )

    llm_service = Mock()

    llm_service.generate.return_value = mock_llm_response(
        "Comprehensive coverage pays for damage "
        "caused by theft, fire and hail."
    )

    source_attribution = Mock()

    source_attribution.build_sources.return_value = [
        {
            "source": "policy.pdf",
            "page": 2,
            "chunk": 5,
        }
    ]

    workflow = AgenticWorkflow(
        retrieval_service=retrieval_service,
        prompt_builder=prompt_builder,
        llm_service=llm_service,
        source_attribution=source_attribution,
    )

    state = workflow.invoke(
        question="What is comprehensive coverage?",
    )

    assert (
        state.question
        == "What is comprehensive coverage?"
    )

    assert (
        state.answer
        == "Comprehensive coverage pays for damage "
        "caused by theft, fire and hail."
    )

    assert len(state.retrieved_chunks) == 1

    assert state.sources == [
        {
            "source": "policy.pdf",
            "page": 2,
            "chunk": 5,
        }
    ]

    retrieval_service.retrieve.assert_called_once()

    prompt_builder.build_prompt.assert_called_once()

    llm_service.generate.assert_called_once()

    source_attribution.build_sources.assert_called_once()

def mock_llm_response(answer: str) -> LLMResponse:
    return LLMResponse(
        answer=answer,
        provider="OpenAI",
        model="gpt-4.1-mini",
        prompt_tokens=125,
        completion_tokens=28,
        total_tokens=153,
        finish_reason="stop",
        latency_ms=187.45,
        retry_count=0,
    )