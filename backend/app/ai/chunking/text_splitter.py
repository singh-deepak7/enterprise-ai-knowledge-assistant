from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings


def create_text_splitter() -> RecursiveCharacterTextSplitter:
    """
    Create the default text splitter used by the ingestion pipeline.
    """

    return RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )