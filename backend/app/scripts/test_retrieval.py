from app.ai.retrieval.retrieval_service import RetrievalService

service = RetrievalService()

results = service.retrieve(
    query="What is collision coverage?",
    top_k=3,
)

print()

for index, doc in enumerate(results, start=1):
    print("=" * 80)
    print(f"Result {index}")
    print("=" * 80)

    print(doc.page_content[:500])

    print()

    print(doc.metadata)