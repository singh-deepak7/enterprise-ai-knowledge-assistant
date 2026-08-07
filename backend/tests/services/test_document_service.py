from unittest.mock import AsyncMock, Mock

import pytest

from app.repositories.document_repository import DocumentRecord
from app.schemas.storage import StorageResult
from app.services.document_service import DocumentService
from pathlib import Path

from app.repositories.document_repository import DocumentRecord


@pytest.mark.asyncio
async def test_upload_indexes_document() -> None:
    validation_service = AsyncMock()
    storage_service = AsyncMock()
    indexing_service = Mock()
    document_repository = Mock()
    vector_store_service = Mock()

    storage_service.save.return_value = StorageResult(
        document_id="123",
        original_filename="sample.pdf",
        stored_filename="abc123.pdf",
        file_path="/tmp/abc123.pdf",
        content_type="application/pdf",
        size_bytes=1024,
    )

    indexing_service.index_document.return_value = 8

    service = DocumentService(
        validation_service=validation_service,
        storage_service=storage_service,
        document_repository=document_repository,
        vector_store_service=vector_store_service,
        indexing_service=indexing_service,
    )

    file = Mock()

    result = await service.upload(file)

    validation_service.validate.assert_awaited_once_with(file)
    storage_service.save.assert_awaited_once_with(file)

    indexing_service.index_document.assert_called_once_with(
        file_path="/tmp/abc123.pdf",
        document_id="123",
        original_filename="sample.pdf",
    )

    document_repository.save.assert_called_once_with(
        DocumentRecord(
            document_id="123",
            original_filename="sample.pdf",
            stored_filename="abc123.pdf",
            file_path="/tmp/abc123.pdf",
            content_type="application/pdf",
            size_bytes=1024,
        )
    )

    assert result.document_id == "123"
    assert result.original_filename == "sample.pdf"


def test_delete_document(
    tmp_path: Path,
) -> None:
    validation_service = Mock()
    storage_service = Mock()
    indexing_service = Mock()
    document_repository = Mock()
    vector_store_service = Mock()

    file_path = tmp_path / "policy.pdf"
    file_path.write_text(
        "test document",
        encoding="utf-8",
    )

    record = DocumentRecord(
        document_id="doc-123",
        original_filename="policy.pdf",
        stored_filename="stored-policy.pdf",
        file_path=str(file_path),
        content_type="application/pdf",
        size_bytes=1024,
    )

    document_repository.get.return_value = record

    service = DocumentService(
        validation_service=validation_service,
        storage_service=storage_service,
        document_repository=document_repository,
        vector_store_service=vector_store_service,
        indexing_service=indexing_service,
    )

    result = service.delete(
        "doc-123"
    )

    assert result is True

    vector_store_service.delete_by_document_id.assert_called_once_with(
        "doc-123"
    )

    assert not file_path.exists()

    document_repository.delete.assert_called_once_with(
        "doc-123"
    )

def test_delete_unknown_document() -> None:
    validation_service = Mock()
    storage_service = Mock()
    indexing_service = Mock()
    document_repository = Mock()
    vector_store_service = Mock()

    document_repository.get.return_value = None

    service = DocumentService(
        validation_service=validation_service,
        storage_service=storage_service,
        document_repository=document_repository,
        vector_store_service=vector_store_service,
        indexing_service=indexing_service,
    )

    result = service.delete(
        "missing"
    )

    assert result is False

    vector_store_service.delete_by_document_id.assert_not_called()
    document_repository.delete.assert_not_called()

def test_delete_document_when_file_is_missing(
    tmp_path: Path,
) -> None:
    validation_service = Mock()
    storage_service = Mock()
    indexing_service = Mock()
    document_repository = Mock()
    vector_store_service = Mock()

    missing_file = tmp_path / "missing.pdf"

    document_repository.get.return_value = DocumentRecord(
        document_id="doc-123",
        original_filename="policy.pdf",
        stored_filename="stored-policy.pdf",
        file_path=str(missing_file),
        content_type="application/pdf",
        size_bytes=1024,
    )

    service = DocumentService(
        validation_service=validation_service,
        storage_service=storage_service,
        document_repository=document_repository,
        vector_store_service=vector_store_service,
        indexing_service=indexing_service,
    )

    result = service.delete(
        "doc-123"
    )

    assert result is True

    vector_store_service.delete_by_document_id.assert_called_once_with(
        "doc-123"
    )

    document_repository.delete.assert_called_once_with(
        "doc-123"
    )