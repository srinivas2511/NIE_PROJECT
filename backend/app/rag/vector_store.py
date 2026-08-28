from dataclasses import dataclass
from functools import lru_cache

import chromadb

from app.core.config import settings
from app.rag.embeddings import embed

COLLECTION_NAME = "enterprise_documents"


@dataclass
class RetrievedChunk:
    text: str
    source: str
    distance: float


@lru_cache(maxsize=1)
def _get_client() -> chromadb.HttpClient:
    return chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)


def get_collection():
    return _get_client().get_or_create_collection(COLLECTION_NAME)


def upsert_documents(ids: list[str], texts: list[str], sources: list[str]) -> None:
    collection = get_collection()
    collection.upsert(
        ids=ids,
        embeddings=embed(texts),
        documents=texts,
        metadatas=[{"source": source} for source in sources],
    )


def query(text: str, n_results: int = 3) -> list[RetrievedChunk]:
    collection = get_collection()
    result = collection.query(query_embeddings=embed([text]), n_results=n_results)

    documents = result.get("documents") or [[]]
    metadatas = result.get("metadatas") or [[]]
    distances = result.get("distances") or [[]]

    return [
        RetrievedChunk(text=doc, source=meta.get("source", "unknown"), distance=dist)
        for doc, meta, dist in zip(documents[0], metadatas[0], distances[0])
    ]
