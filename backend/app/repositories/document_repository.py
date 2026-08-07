from __future__ import annotations

from dataclasses import dataclass
from threading import Lock


@dataclass(frozen=True, slots=True)
class DocumentRecord:
    document_id: str
    original_filename: str
    stored_filename: str
    file_path: str
    content_type: str
    size_bytes: int


class DocumentRepository:
    """
    Thread-safe in-memory registry of uploaded documents.

    This is intentionally infrastructure-light for now.
    It can later be replaced by a persistent database
    implementation without changing the service/API contract.
    """

    def __init__(self) -> None:
        self._documents: dict[str, DocumentRecord] = {}
        self._lock = Lock()

    def save(
        self,
        record: DocumentRecord,
    ) -> None:
        with self._lock:
            self._documents[
                record.document_id
            ] = record

    def list_all(
        self,
    ) -> list[DocumentRecord]:
        with self._lock:
            return list(
                self._documents.values()
            )

    def get(
        self,
        document_id: str,
    ) -> DocumentRecord | None:
        with self._lock:
            return self._documents.get(
                document_id
            )

    def delete(
        self,
        document_id: str,
    ) -> DocumentRecord | None:
        with self._lock:
            return self._documents.pop(
                document_id,
                None,
            )