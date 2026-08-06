from unittest.mock import Mock

from langchain_core.documents import Document

from app.ai.retrieval.rag_service import RAGService


def test_generate_answer_success() -> None:
    """
    Test that RAGService orchestrates retrieval, prompt building,
    and LLM generation successfully.
    """

    # Arrange
    documents = [
        Document(
            page_content="Employees receive 20 vacation days.",
            metadata={
                "source": "employee_handbook.pdf",
                "page": 15,
            },
        )
    ]

    retrieval_service = Mock()
    retrieval_service.retrieve.return_value = documents

    prompt_builder = Mock()
    prompt_builder.build_prompt.return_value = "Generated Prompt"

    llm_service = Mock()
    llm_service.generate.return_value = "Generated Answer"

    rag_service = RAGService(
        retrieval_service=retrieval_service,
        prompt_builder=prompt_builder,
        llm_service=llm_service,
    )

    # Act
    result = rag_service.generate_answer(
        question="How many vacation days do employees receive?",
        top_k=5,
    )

    # Assert
    retrieval_service.retrieve.assert_called_once_with(
        query="How many vacation days do employees receive?",
        top_k=5,
    )

    prompt_builder.build_prompt.assert_called_once_with(
        question="How many vacation days do employees receive?",
        documents=documents,
    )

    llm_service.generate.assert_called_once_with(
        prompt="Generated Prompt",
    )

    assert result["answer"] == "Generated Answer"
    assert result["sources"] == documents


def test_generate_answer_with_no_documents() -> None:
    """
    Test RAGService when retrieval returns no documents.
    """

    retrieval_service = Mock()
    retrieval_service.retrieve.return_value = []

    prompt_builder = Mock()
    prompt_builder.build_prompt.return_value = "Empty Context Prompt"

    llm_service = Mock()
    llm_service.generate.return_value = (
        "I couldn't find that information in the provided documents."
    )

    rag_service = RAGService(
        retrieval_service=retrieval_service,
        prompt_builder=prompt_builder,
        llm_service=llm_service,
    )

    result = rag_service.generate_answer(
        question="Unknown question",
    )

    retrieval_service.retrieve.assert_called_once()

    prompt_builder.build_prompt.assert_called_once_with(
        question="Unknown question",
        documents=[],
    )

    llm_service.generate.assert_called_once_with(
        prompt="Empty Context Prompt",
    )

    assert result["answer"] == (
        "I couldn't find that information in the provided documents."
    )
    assert result["sources"] == []


def test_generate_answer_propagates_exception() -> None:
    """
    Test that exceptions raised during retrieval are propagated.
    """

    retrieval_service = Mock()
    retrieval_service.retrieve.side_effect = RuntimeError(
        "Vector store unavailable"
    )

    rag_service = RAGService(
        retrieval_service=retrieval_service,
        prompt_builder=Mock(),
        llm_service=Mock(),
    )

    try:
        rag_service.generate_answer("Test question")
        assert False, "Expected RuntimeError"
    except RuntimeError as exc:
        assert str(exc) == "Vector store unavailable"