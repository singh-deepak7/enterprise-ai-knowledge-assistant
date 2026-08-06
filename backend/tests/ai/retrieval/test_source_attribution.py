from langchain_core.documents import Document

from app.ai.retrieval.source_attribution import (
    SourceAttribution,
)


def test_build_sources() -> None:
    service = SourceAttribution()

    documents = [
        Document(
            page_content="Vacation policy",
            metadata={
                "source": "employee.pdf",
                "page": 12,
                "chunk": 4,
            },
        ),
        Document(
            page_content="Benefits",
            metadata={
                "source": "benefits.pdf",
                "page": 5,
                "chunk": 1,
            },
        ),
    ]

    result = service.build_sources(documents)

    assert result == [
        {
            "source": "employee.pdf",
            "page": 12,
            "chunk": 4,
        },
        {
            "source": "benefits.pdf",
            "page": 5,
            "chunk": 1,
        },
    ]


def test_build_sources_empty() -> None:
    service = SourceAttribution()

    assert service.build_sources([]) == []


def test_build_sources_missing_metadata() -> None:
    service = SourceAttribution()

    documents = [
        Document(
            page_content="Hello",
            metadata={},
        )
    ]

    result = service.build_sources(documents)

    assert result == [
        {
            "source": "Unknown",
            "page": None,
            "chunk": None,
        }
    ]