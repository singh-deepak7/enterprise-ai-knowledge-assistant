from langsmith import Client

from app.ai.evaluation.dataset import EVALUATION_CASES


DATASET_NAME = "enterprise-ai-rag-evaluation"


def create_evaluation_dataset() -> None:
    client = Client()

    existing_datasets = list(
        client.list_datasets(
            dataset_name=DATASET_NAME,
        )
    )

    if existing_datasets:
        print(
            f"Dataset '{DATASET_NAME}' already exists. "
            "Skipping creation."
        )
        return

    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description=(
            "Golden evaluation dataset for the Enterprise AI "
            "Knowledge Assistant RAG workflow."
        ),
    )

    for case in EVALUATION_CASES:
        client.create_example(
            dataset_id=dataset.id,
            inputs={
                "question": case.question,
            },
            outputs={
                "expected_answer": case.expected_answer,
                "expected_source_contains": (
                    case.expected_source_contains
                ),
            },
        )

    print(
        f"Created dataset '{DATASET_NAME}' "
        f"with {len(EVALUATION_CASES)} examples."
    )


if __name__ == "__main__":
    create_evaluation_dataset()