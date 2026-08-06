from langchain_core.documents import Document

from app.ai.agentic.graph_state import GraphState


def test_graph_state_defaults():
    state = GraphState(question="What is comprehensive coverage?")

    assert state.question == "What is comprehensive coverage?"

    assert state.intent == "general_qa"
    assert state.retrieval_strategy == "hybrid"
    assert state.top_k == 5
    assert state.requires_retrieval is True

    assert state.retrieved_chunks == []
    assert state.prompt == ""
    assert state.answer == ""

    assert state.validated is False
    assert state.confidence_score == 0.0

    assert state.sources == []
    assert state.metadata == {}


def test_graph_state_custom_values():
    state = GraphState(
        question="Compare policies",
        intent="comparison",
        retrieval_strategy="semantic",
        top_k=8,
        requires_retrieval=True,
        validated=True,
        confidence_score=0.94,
    )

    assert state.intent == "comparison"
    assert state.retrieval_strategy == "semantic"
    assert state.top_k == 8
    assert state.requires_retrieval is True
    assert state.validated is True
    assert state.confidence_score == 0.94


def test_graph_state_stores_retrieved_chunks():
    doc = Document(page_content="Coverage text")

    state = GraphState(
        question="Test",
        retrieved_chunks=[doc],
    )

    assert len(state.retrieved_chunks) == 1
    assert state.retrieved_chunks[0].page_content == "Coverage text"


def test_graph_state_stores_sources():
    sources = [
        {
            "source": "policy.pdf",
            "page": 4,
        }
    ]

    state = GraphState(
        question="Test",
        sources=sources,
    )

    assert state.sources == sources


def test_graph_state_stores_metadata():
    metadata = {
        "request_id": "abc123",
        "planner_ms": 8,
    }

    state = GraphState(
        question="Test",
        metadata=metadata,
    )

    assert state.metadata == metadata


def test_graph_state_prompt_and_answer():
    state = GraphState(
        question="Test",
        prompt="Prompt",
        answer="Answer",
    )

    assert state.prompt == "Prompt"
    assert state.answer == "Answer"