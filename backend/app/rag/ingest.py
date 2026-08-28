from pathlib import Path

from app.rag.vector_store import upsert_documents

DOCUMENTS_DIR = Path(__file__).parent / "documents"


def ingest_documents() -> int:
    """Embed and upsert every document in documents/ into the vector store.

    Keyed by filename, so re-running (e.g. on every backend startup) is
    idempotent -- it just re-upserts the same ids.
    """
    paths = sorted(DOCUMENTS_DIR.glob("*.md"))
    if not paths:
        return 0

    ids = [path.name for path in paths]
    texts = [path.read_text(encoding="utf-8") for path in paths]
    sources = ids

    upsert_documents(ids=ids, texts=texts, sources=sources)
    return len(paths)
