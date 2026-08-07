from app.repositories.document_repository import (
    DocumentRecord,
    DocumentRepository,
)


def build_record(
    document_id: str = "doc-1",
) -> DocumentRecord:
    return DocumentRecord(
        document_id=document_id,
        original_filename="policy.pdf",
        stored_filename="stored-policy.pdf",
        file_path="/tmp/stored-policy.pdf",
        content_type="application/pdf",
        size_bytes=1024,
        content_hash="test-hash",
    )


def test_save_and_get_document(tmp_path,) -> None:
    repository = DocumentRepository(
        tmp_path / "documents.db"
    )

    record = build_record()

    repository.save(record)

    assert repository.get("doc-1") == record


def test_list_documents(tmp_path,) -> None:
    repository = DocumentRepository(
        tmp_path / "documents.db"
    )

    first = build_record(
        "doc-1"
    )

    second = build_record(
        "doc-2"
    )

    repository.save(first)
    repository.save(second)

    assert repository.list_all() == [
        first,
        second,
    ]


def test_delete_document(tmp_path,) -> None:
    repository = DocumentRepository(
        tmp_path / "documents.db"
    )

    record = build_record()

    repository.save(record)

    deleted = repository.delete(
        "doc-1"
    )

    assert deleted == record
    assert repository.get(
        "doc-1"
    ) is None


def test_delete_unknown_document(tmp_path,) -> None:
    repository = DocumentRepository(
        tmp_path / "documents.db"
    )

    assert repository.delete(
        "missing"
    ) is None

def test_get_by_content_hash(
    tmp_path,
) -> None:
    repository = DocumentRepository(
        tmp_path / "documents.db"
    )

    record = DocumentRecord(
        document_id="doc-123",
        original_filename="policy.pdf",
        stored_filename="stored-policy.pdf",
        file_path="/tmp/stored-policy.pdf",
        content_type="application/pdf",
        size_bytes=1024,
        content_hash="sha256-test-hash",
    )

    repository.save(record)

    result = repository.get_by_content_hash(
        "sha256-test-hash"
    )

    assert result == record

def test_get_by_content_hash_returns_none(
    tmp_path,
) -> None:
    repository = DocumentRepository(
        tmp_path / "documents.db"
    )

    result = repository.get_by_content_hash(
        "missing-hash"
    )

    assert result is None