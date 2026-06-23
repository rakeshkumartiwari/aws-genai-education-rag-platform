import json
import re
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = ROOT / "data" / "course_catalog.md"
STORE_FILE = ROOT / "data" / "vector_store.json"


def chunk_markdown(text: str):
    sections = re.split(r"\n(?=## )", text)
    chunks = []
    for index, section in enumerate(sections):
        clean = section.strip()
        if clean:
            chunks.append({
                "id": f"course_catalog.md::chunk-{index + 1}",
                "text": clean
            })
    return chunks


def build_store():
    text = SOURCE_FILE.read_text(encoding="utf-8")
    chunks = chunk_markdown(text)
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform([chunk["text"] for chunk in chunks])

    store = {
        "vocabulary": vectorizer.vocabulary_,
        "idf": vectorizer.idf_.tolist(),
        "chunks": chunks,
        "matrix": matrix.toarray().tolist()
    }
    STORE_FILE.write_text(json.dumps(store, indent=2), encoding="utf-8")
    return store


if __name__ == "__main__":
    build_store()
    print(f"Vector store created at {STORE_FILE}")
