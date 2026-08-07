from unittest.mock import AsyncMock, Mock

import pytest

from app.repositories.document_repository import DocumentRecord
from app.schemas.storage import StorageResult
from app.services.document_service import DocumentService


@pytest.mark.asyncio
async def test_upload_indexes_document() -> None:
    validation_service = AsyncMock()
    storage_service = AsyncMock()
    indexing_service = Mock()
    document_repository = Mock()

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