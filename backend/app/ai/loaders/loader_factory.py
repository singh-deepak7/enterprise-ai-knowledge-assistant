from pathlib import Path

from app.ai.loaders.base_loader import BaseLoader
from app.ai.loaders.csv_loader import CsvLoader
from app.ai.loaders.excel_loader import ExcelLoader
from app.ai.loaders.pdf_loader import PdfLoader
from app.ai.loaders.text_loader import TxtLoader


class LoaderFactory:
    """
    Factory responsible for selecting the appropriate document loader
    based on the file extension.
    """

    _loaders: dict[str, type[BaseLoader]] = {
        ".pdf": PdfLoader,
        ".txt": TxtLoader,
        ".csv": CsvLoader,
        ".xlsx": ExcelLoader,
    }

    @classmethod
    def get_loader(cls, file_path: str) -> BaseLoader:
        file_path = Path(file_path)
        extension = file_path.suffix.lower()

        loader_class = cls._loaders.get(extension)

        if loader_class is None:
            supported = ", ".join(sorted(cls._loaders.keys()))
            raise ValueError(
                f"Unsupported file type '{extension}'. "
                f"Supported file types: {supported}"
            )

        return loader_class()