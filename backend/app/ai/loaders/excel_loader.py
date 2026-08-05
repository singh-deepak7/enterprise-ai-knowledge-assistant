from pathlib import Path

import pandas as pd
from langchain_core.documents import Document

from app.ai.loaders.base_loader import BaseLoader
from app.core.logging import get_logger

logger = get_logger(__name__)


class ExcelLoader(BaseLoader):
    """
    Loads Excel workbooks into LangChain Document objects.

    Each worksheet is processed independently and every row
    becomes a separate LangChain Document.
    """

    def load(self, file_path: Path) -> list[Document]:
        logger.info("Loading Excel document: %s", file_path.name)

        workbook = pd.read_excel(
            file_path,
            sheet_name=None,
        )

        documents: list[Document] = []

        for sheet_name, dataframe in workbook.items():

            logger.info(
                "Processing worksheet '%s' (%d rows)",
                sheet_name,
                len(dataframe),
            )

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
                        "sheet": sheet_name,
                        "row_index": index,
                        "row_number": index + 1,
                    },
                )

                documents.append(document)

        logger.info(
            "Loaded %d documents from workbook '%s'",
            len(documents),
            file_path.name,
        )

        return documents