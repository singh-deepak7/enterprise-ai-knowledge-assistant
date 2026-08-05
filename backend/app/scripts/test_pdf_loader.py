from pathlib import Path

from app.ai.loaders.text_loader import TxtLoader
from app.ai.loaders.pdf_loader import PdfLoader
from app.ai.loaders.csv_loader import CsvLoader


def main():
    from pathlib import Path

    BASE_DIR = Path(__file__).resolve().parents[2]
    pdf_path = BASE_DIR / "app" / "sample_docs" / "sample.pdf"

    loader = PdfLoader()

    pdf_documents = loader.load(pdf_path)

    print("=" * 80)
    print(f"Total Pages: {len(pdf_documents)}")
    print("=" * 80)

    for i, doc in enumerate(pdf_documents, start=1):
        print(f"\n----- Document {i} -----")
        print("Metadata:")
        print(doc.metadata)

        print("\nContent Preview:")
        print(doc.page_content[:300])
        print("-" * 80)

    textLoader = TxtLoader()
    text_path = BASE_DIR / "app" / "sample_docs" / "sample.txt"
    text_documents = textLoader.load(Path(text_path))

    print(text_documents[0].metadata)
    print(text_documents[0].page_content)



    csvLoader = CsvLoader()
    csv_path = BASE_DIR / "app" / "sample_docs" / "sample.csv"
    csv_documents = csvLoader.load(Path(csv_path))

    print(f"Documents: {len(csv_documents)}")

    for doc in csv_documents:
        print("=" * 60)
        print(doc.metadata)
        print(doc.page_content)


if __name__ == "__main__":
    main()