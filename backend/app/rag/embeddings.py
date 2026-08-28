from functools import lru_cache

from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def embed(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    return model.encode(texts, convert_to_numpy=True).tolist()
