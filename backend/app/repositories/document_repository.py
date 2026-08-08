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
    content_hash: str = ""
    uploaded_at: str = ""
    chunk_count: int = 0
    status: str = "indexed"


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
        """
        Open a SQLite connection.
        """

        connection = sqlite3.connect(
            self._database_path,
        )

        connection.row_factory = sqlite3.Row

        return connection

    def _initialize_database(
        self,
    ) -> None:
        """
        Create the documents table and apply lightweight
        schema migrations when required.
        """

        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    original_filename TEXT NOT NULL,
                    stored_filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    content_hash TEXT,
                    uploaded_at TEXT,
                    chunk_count INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'indexed'
                )
                """
            )

            columns = connection.execute(
                """
                PRAGMA table_info(documents)
                """
            ).fetchall()

            column_names = {
                column["name"]
                for column in columns
            }

            if "content_hash" not in column_names:
                connection.execute(
                    """
                    ALTER TABLE documents
                    ADD COLUMN content_hash TEXT
                    """
                )

            if "uploaded_at" not in column_names:
                connection.execute(
                    """
                    ALTER TABLE documents
                    ADD COLUMN uploaded_at TEXT
                    """
                )

            if "chunk_count" not in column_names:
                connection.execute(
                    """
                    ALTER TABLE documents
                    ADD COLUMN chunk_count INTEGER NOT NULL DEFAULT 0
                    """
                )

            if "status" not in column_names:
                connection.execute(
                    """
                    ALTER TABLE documents
                    ADD COLUMN status TEXT NOT NULL DEFAULT 'indexed'
                    """
                )

    def save(
        self,
        record: DocumentRecord,
    ) -> None:
        """
        Insert or update document metadata.
        """

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    document_id,
                    original_filename,
                    stored_filename,
                    file_path,
                    content_type,
                    size_bytes,
                    content_hash,
                    uploaded_at,
                    chunk_count,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(document_id)
                DO UPDATE SET
                    original_filename = excluded.original_filename,
                    stored_filename = excluded.stored_filename,
                    file_path = excluded.file_path,
                    content_type = excluded.content_type,
                    size_bytes = excluded.size_bytes,
                    content_hash = excluded.content_hash,
                    uploaded_at = excluded.uploaded_at,
                    chunk_count = excluded.chunk_count,
                    status = excluded.status
                """,
                (
                    record.document_id,
                    record.original_filename,
                    record.stored_filename,
                    record.file_path,
                    record.content_type,
                    record.size_bytes,
                    record.content_hash,
                    record.uploaded_at,
                    record.chunk_count,
                    record.status,
                ),
            )

    def list_all(
        self,
    ) -> list[DocumentRecord]:
        """
        Return all registered documents.
        """

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    document_id,
                    original_filename,
                    stored_filename,
                    file_path,
                    content_type,
                    size_bytes,
                    content_hash,
                    uploaded_at,
                    chunk_count,
                    status
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
        """
        Return a document by document ID.
        """

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    document_id,
                    original_filename,
                    stored_filename,
                    file_path,
                    content_type,
                    size_bytes,
                    content_hash,
                    uploaded_at,
                    chunk_count,
                    status
                FROM documents
                WHERE document_id = ?
                """,
                (document_id,),
            ).fetchone()

        if row is None:
            return None

        return self._to_record(row)

    def get_by_content_hash(
        self,
        content_hash: str,
    ) -> DocumentRecord | None:
        """
        Return a document matching the supplied content hash.
        """

        if not content_hash:
            return None

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    document_id,
                    original_filename,
                    stored_filename,
                    file_path,
                    content_type,
                    size_bytes,
                    content_hash,
                    uploaded_at,
                    chunk_count,
                    status
                FROM documents
                WHERE content_hash = ?
                LIMIT 1
                """,
                (content_hash,),
            ).fetchone()

        if row is None:
            return None

        return self._to_record(row)

    def delete(
        self,
        document_id: str,
    ) -> DocumentRecord | None:
        """
        Delete a document metadata record.

        Returns the deleted record when it existed.
        """

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
        """
        Convert a SQLite row into a DocumentRecord.
        """

        return DocumentRecord(
            document_id=row["document_id"],
            original_filename=row["original_filename"],
            stored_filename=row["stored_filename"],
            file_path=row["file_path"],
            content_type=row["content_type"],
            size_bytes=row["size_bytes"],
            content_hash=row["content_hash"] or "",
            uploaded_at=row["uploaded_at"] or "",
            chunk_count=row["chunk_count"] or 0,
            status=row["status"] or "indexed",
        )