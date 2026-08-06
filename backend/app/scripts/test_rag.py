import logging

from app.ai.retrieval.rag_service import RAGService

logging.basicConfig(level=logging.INFO)


def main() -> None:
    rag_service = RAGService()

    question = (
        "What information is available in the uploaded documents?"
    )

    result = rag_service.generate_answer(
        question=question,
        top_k=5,
    )

    print("\n========== ANSWER ==========\n")
    print(result["answer"])

    print("\n========== SOURCES ==========\n")

    for source in result["sources"]:
        print(source)


if __name__ == "__main__":
    main()