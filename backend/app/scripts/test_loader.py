from pathlib import Path

from app.ai.loaders.loader_factory import LoaderFactory

files = [
    "sample.pdf",
    "sample.txt",
    "sample.csv",
    "sample.xlsx",

]

BASE_DIR = Path(__file__).resolve().parents[2]

for file in files:
    loader = LoaderFactory.get_loader(Path(BASE_DIR / "app" / "sample_docs" / file))
    print(file, "->", type(loader).__name__)