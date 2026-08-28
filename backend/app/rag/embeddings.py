from functools import lru_cache

from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def embed(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    # Normalized so L2 distance is bounded to [0, 2] -- FR-6 confidence scoring
    # (app/rag/pipeline.py) relies on that bound.
    return model.encode(texts, convert_to_numpy=True, normalize_embeddings=True).tolist()
