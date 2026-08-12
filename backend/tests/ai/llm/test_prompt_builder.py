from langchain_core.documents import Document

from app.ai.llm.prompt_builder import PromptBuilder
from app.ai.memory.conversation_memory import ConversationTurn


def test_build_prompt_with_single_document():
    builder = PromptBuilder()

    documents = [
        Document(
            page_content="Comprehensive coverage protects against theft.",
            metadata={
                "source": "policy.pdf",
                "page": 2,
            },
        )
    ]

    prompt = builder.build_prompt(
        question="What does comprehensive coverage protect against?",
        documents=documents,
    )

    assert "Enterprise AI Knowledge & Decision Support Assistant" in prompt
    assert "Retrieved Context" in prompt
    assert "policy.pdf" in prompt
    assert "Page: 2" in prompt
    assert "Comprehensive coverage protects against theft." in prompt
    assert (
        "What does comprehensive coverage protect against?"
        in prompt
    )
    assert "Conversation History" not in prompt


def test_build_prompt_with_multiple_documents():
    builder = PromptBuilder()

    documents = [
        Document(
            page_content="Collision coverage pays for collision damage.",
            metadata={
                "source": "policy.pdf",
                "page": 4,
            },
        ),
        Document(
            page_content="Comprehensive coverage pays for theft.",
            metadata={
                "source": "policy.pdf",
                "page": 5,
            },
        ),
    ]

    prompt = builder.build_prompt(
        question="Compare collision and comprehensive coverage.",
        documents=documents,
    )

    assert "[Document 1]" in prompt
    assert "[Document 2]" in prompt
    assert "Collision coverage pays for collision damage." in prompt
    assert "Comprehensive coverage pays for theft." in prompt


def test_build_prompt_with_no_documents():
    builder = PromptBuilder()

    prompt = builder.build_prompt(
        question="What is covered?",
        documents=[],
    )

    assert "No relevant documents were retrieved." in prompt
    assert "What is covered?" in prompt


def test_build_prompt_with_conversation_history():
    builder = PromptBuilder()

    history = [
        ConversationTurn(
            role="user",
            content="What is comprehensive coverage?",
        ),
        ConversationTurn(
            role="assistant",
            content="It covers non-collision losses.",
        ),
    ]

    prompt = builder.build_prompt(
        question="Does it cover hail damage?",
        documents=[],
        conversation_history=history,
    )

    assert "Conversation History" in prompt
    assert "User: What is comprehensive coverage?" in prompt
    assert "Assistant: It covers non-collision losses." in prompt
    assert "Does it cover hail damage?" in prompt


def test_build_prompt_without_conversation_history():
    builder = PromptBuilder()

    prompt = builder.build_prompt(
        question="Hello",
        documents=[],
        conversation_history=None,
    )

    assert "Conversation History" not in prompt


def test_format_conversation():
    builder = PromptBuilder()

    history = [
        ConversationTurn(
            role="user",
            content="Question",
        ),
        ConversationTurn(
            role="assistant",
            content="Answer",
        ),
    ]

    formatted = builder._format_conversation(history)

    assert formatted == (
        "User: Question\n"
        "Assistant: Answer"
    )


def test_format_empty_conversation():
    builder = PromptBuilder()

    assert builder._format_conversation([]) == ""


def test_prompt_contains_source_metadata():
    builder = PromptBuilder()

    documents = [
        Document(
            page_content="Example content.",
            metadata={
                "source": "claims.pdf",
                "page": 12,
            },
        )
    ]

    prompt = builder.build_prompt(
        question="Example?",
        documents=documents,
    )

    assert "Source: claims.pdf" in prompt
    assert "Page: 12" in prompt


def test_prompt_uses_default_metadata_when_missing():
    builder = PromptBuilder()

    documents = [
        Document(
            page_content="Example content.",
            metadata={},
        )
    ]

    prompt = builder.build_prompt(
        question="Example?",
        documents=documents,
    )

    assert "Source: Unknown" in prompt
    assert "Page: N/A" in prompt