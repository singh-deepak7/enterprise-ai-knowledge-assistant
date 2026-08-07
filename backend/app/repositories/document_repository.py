from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from app.core.config import settings


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
    Persistent SQLite repository for document metadata.
    """

    def __init__(
        self,
        database_path: str | Path | None = None,
    ) -> None:
        self._database_path = Path(
            database_path or settings.DOCUMENT_DB_PATH
        )

        self._database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_database()

    def _connect(
        self,
    ) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self._database_path,
        )

        connection.row_factory = sqlite3.Row

        return connection

    def _initialize_database(
        self,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    original_filename TEXT NOT NULL,
                    stored_filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL
                )
                """
            )

    def save(
        self,
        record: DocumentRecord,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    document_id,
                    original_filename,
                    stored_filename,
                    file_path,
                    content_type,
                    size_bytes
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(document_id)
                DO UPDATE SET
                    original_filename = excluded.original_filename,
                    stored_filename = excluded.stored_filename,
                    file_path = excluded.file_path,
                    content_type = excluded.content_type,
                    size_bytes = excluded.size_bytes
                """,
                (
                    record.document_id,
                    record.original_filename,
                    record.stored_filename,
                    record.file_path,
                    record.content_type,
                    record.size_bytes,
                ),
            )

    def list_all(
        self,
    ) -> list[DocumentRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    document_id,
                    original_filename,
                    stored_filename,
                    file_path,
                    content_type,
                    size_bytes
                FROM documents
                ORDER BY original_filename
                """
            ).fetchall()

        return [
            self._to_record(row)
            for row in rows
        ]

    def get(
        self,
        document_id: str,
    ) -> DocumentRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    document_id,
                    original_filename,
                    stored_filename,
                    file_path,
                    content_type,
                    size_bytes
                FROM documents
                WHERE document_id = ?
                """,
                (document_id,),
            ).fetchone()

        if row is None:
            return None

        return self._to_record(row)

    def delete(
        self,
        document_id: str,
    ) -> DocumentRecord | None:
        record = self.get(
            document_id,
        )

        if record is None:
            return None

        with self._connect() as connection:
            connection.execute(
                """
                DELETE FROM documents
                WHERE document_id = ?
                """,
                (document_id,),
            )

        return record

    @staticmethod
    def _to_record(
        row: sqlite3.Row,
    ) -> DocumentRecord:
        return DocumentRecord(
            document_id=row["document_id"],
            original_filename=row["original_filename"],
            stored_filename=row["stored_filename"],
            file_path=row["file_path"],
            content_type=row["content_type"],
            size_bytes=row["size_bytes"],
        )