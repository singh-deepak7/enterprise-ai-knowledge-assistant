from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings
from app.core.logging import logger
from app.schemas.storage import StorageResult


class StorageService:
    """
    Handles storage of uploaded documents.

    Responsibilities:
    - Create upload directory
    - Generate unique filename
    - Save uploaded file
    - Return storage metadata
    """

    def __init__(self) -> None:
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, file: UploadFile) -> StorageResult:
        """
        Save an uploaded file to local storage.

        Args:
            file: FastAPI UploadFile

        Returns:
            StorageResult
        """

        document_id = str(uuid4())

        extension = Path(file.filename).suffix

        stored_filename = f"{document_id}{extension}"

        destination = self.upload_dir / stored_filename

        logger.info(
            "Saving file '%s' as '%s'",
            file.filename,
            stored_filename,
        )

        contents = await file.read()

        destination.write_bytes(contents)

        return StorageResult(
            document_id=document_id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_path=str(destination),
            content_type=file.content_type,
            size_bytes=len(contents),
        )