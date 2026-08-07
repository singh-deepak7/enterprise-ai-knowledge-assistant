from fastapi.testclient import TestClient

from app.dependencies import get_document_repository
from app.main import app
from app.repositories.document_repository import (
    DocumentRecord,
    DocumentRepository,
)

client = TestClient(app)


def test_list_documents(
    tmp_path,
) -> None:
    repository = DocumentRepository(
        tmp_path / "documents.db"
    )

    repository.save(
        DocumentRecord(
            document_id="doc-123",
            original_filename="policy.pdf",
            stored_filename="stored-policy.pdf",
            file_path="/tmp/stored-policy.pdf",
            content_type="application/pdf",
            size_bytes=1024,
        )
    )

    app.dependency_overrides[
        get_document_repository
    ] = lambda: repository

    try:
        response = client.get(
            "/api/v1/documents"
        )

        assert response.status_code == 200

        assert response.json() == {
            "documents": [
                {
                    "document_id": "doc-123",
                    "original_filename": "policy.pdf",
                    "content_type": "application/pdf",
                    "size_bytes": 1024,
                }
            ]
        }
    finally:
        app.dependency_overrides.clear()