from pathlib import Path

from app.ai.loaders.text_loader import TxtLoader
from app.ai.loaders.pdf_loader import PdfLoader


def main():
    from pathlib import Path

    BASE_DIR = Path(__file__).resolve().parents[2]
    pdf_path = BASE_DIR / "app" / "sample_docs" / "sample.pdf"

    loader = PdfLoader()

    documents = loader.load(pdf_path)

    print("=" * 80)
    print(f"Total Pages: {len(documents)}")
    print("=" * 80)

    for i, doc in enumerate(documents, start=1):
        print(f"\n----- Document {i} -----")
        print("Metadata:")
        print(doc.metadata)

        print("\nContent Preview:")
        print(doc.page_content[:300])
        print("-" * 80)

    textLoader = TxtLoader()
    text_path = BASE_DIR / "app" / "sample_docs" / "sample.txt"
    documents = textLoader.load(Path(text_path))

    print(documents[0].metadata)
    print(documents[0].page_content)


if __name__ == "__main__":
    main()