import json
import sys
from pathlib import Path
from typing import List, Dict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parents[1]
STORE_FILE = ROOT / "data" / "vector_store.json"

BLOCKED_PATTERNS = [
    "ignore previous instructions",
    "reveal system prompt",
    "bypass guardrails",
    "forget your rules",
    "act as developer mode"
]


def is_prompt_attack(question: str) -> bool:
    q = question.lower()
    return any(pattern in q for pattern in BLOCKED_PATTERNS)


def load_store() -> Dict:
    if not STORE_FILE.exists():
        raise FileNotFoundError("Run `python src/ingest.py` first.")
    return json.loads(STORE_FILE.read_text(encoding="utf-8"))


def retrieve(question: str, top_k: int = 2) -> List[Dict]:
    store = load_store()
    vectorizer = TfidfVectorizer(stop_words="english", vocabulary=store["vocabulary"])
    vectorizer.fit([chunk["text"] for chunk in store["chunks"]])
    query_vector = vectorizer.transform([question]).toarray()[0]
    matrix = np.array(store["matrix"])
    scores = matrix @ query_vector
    top_indexes = scores.argsort()[::-1][:top_k]
    results = []
    for idx in top_indexes:
        if scores[idx] > 0:
            results.append({"score": float(scores[idx]), **store["chunks"][idx]})
    return results


def answer(question: str) -> str:
    if is_prompt_attack(question):
        return (
            "I cannot follow instructions that try to bypass safety rules or reveal hidden instructions. "
            "Please ask a course-related question."
        )

    hits = retrieve(question)
    if not hits:
        return "I do not know based on the approved course content. Please contact faculty support."

    context = "\n\n".join(hit["text"] for hit in hits)
    sources = "\n".join(f"- {hit['id']}" for hit in hits)
    return (
        "Answer:\n"
        f"Based on the approved course content:\n\n{context}\n\n"
        "Sources:\n"
        f"{sources}"
    )


if __name__ == "__main__":
    user_question = " ".join(sys.argv[1:]) or "What is the grading policy for AI Foundations?"
    print(answer(user_question))
