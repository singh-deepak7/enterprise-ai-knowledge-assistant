from pathlib import Path

import pandas as pd
from langchain_core.documents import Document

from app.ai.loaders.base_loader import BaseLoader
from app.core.logging import get_logger

logger = get_logger(__name__)


class CsvLoader(BaseLoader):
    """
    Loads CSV files into LangChain Document objects.

    Each row in the CSV is converted into a separate Document to improve
    semantic retrieval accuracy.
    """

    def load(self, file_path: Path) -> list[Document]:
        logger.info("Loading CSV document: %s", file_path.name)

        dataframe = pd.read_csv(file_path)

        documents: list[Document] = []

        for index, row in dataframe.iterrows():
            page_content = "\n".join(
                f"{column}: {'' if pd.isna(value) else value}"
                for column, value in row.items()
            )

            document = Document(
                page_content=page_content,
                metadata={
                "filename": file_path.name,
                "extension": file_path.suffix.lower(),
                "source": str(file_path),
                "row_index": index,
                "row_number": index + 1,
            },
            )

            documents.append(document)

        logger.info(
            "Loaded %d rows from CSV '%s'",
            len(documents),
            file_path.name,
        )

        return documents