from fastapi.testclient import TestClient

from app.dependencies import get_document_repository
from app.main import app
from app.repositories.document_repository import (
    DocumentRecord,
    DocumentRepository,
)
from unittest.mock import Mock

from app.dependencies import (
    get_document_repository,
    get_document_service,
)
from app.services.document_service import DocumentService

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

def test_delete_document() -> None:
    service = Mock(
        spec=DocumentService
    )

    service.delete.return_value = True

    app.dependency_overrides[
        get_document_service
    ] = lambda: service

    try:
        response = client.delete(
            "/api/v1/documents/doc-123"
        )

        assert response.status_code == 204
        assert response.content == b""

        service.delete.assert_called_once_with(
            "doc-123"
        )
    finally:
        app.dependency_overrides.clear()

def test_delete_unknown_document() -> None:
    service = Mock(
        spec=DocumentService
    )

    service.delete.return_value = False

    app.dependency_overrides[
        get_document_service
    ] = lambda: service

    try:
        response = client.delete(
            "/api/v1/documents/missing"
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": "Document not found."
        }

        service.delete.assert_called_once_with(
            "missing"
        )
    finally:
        app.dependency_overrides.clear()