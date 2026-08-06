from app.ai.indexing.indexing_service import IndexingService
from pathlib import Path

service = IndexingService()

BASE_DIR = Path(__file__).resolve().parents[2]
pdf_path = BASE_DIR / "app" / "sample_docs" / "sample.pdf"

count = service.index_document(pdf_path)

print(f"Indexed {count} chunks")