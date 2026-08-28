import re
from pathlib import Path

import yaml

from app.rag.vector_store import upsert_documents

DOCUMENTS_DIR = Path(__file__).parent / "documents"
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
DEFAULT_ALLOWED_ROLES = ["employee", "hr", "admin"]


def _parse_document(raw: str) -> tuple[list[str], str]:
    """Split a doc into (allowed_roles, body). Docs without frontmatter default to open access."""
    match = FRONTMATTER_RE.match(raw)
    if not match:
        return DEFAULT_ALLOWED_ROLES, raw

    frontmatter, body = match.groups()
    meta = yaml.safe_load(frontmatter) or {}
    return meta.get("allowed_roles", DEFAULT_ALLOWED_ROLES), body.strip()


def ingest_documents() -> int:
    """Embed and upsert every document in documents/ into the vector store.

    Keyed by filename, so re-running (e.g. on every backend startup) is
    idempotent -- it just re-upserts the same ids.
    """
    paths = sorted(DOCUMENTS_DIR.glob("*.md"))
    if not paths:
        return 0

    ids: list[str] = []
    texts: list[str] = []
    sources: list[str] = []
    allowed_roles_list: list[list[str]] = []

    for path in paths:
        allowed_roles, body = _parse_document(path.read_text(encoding="utf-8"))
        ids.append(path.name)
        texts.append(body)
        sources.append(path.name)
        allowed_roles_list.append(allowed_roles)

    upsert_documents(ids=ids, texts=texts, sources=sources, allowed_roles=allowed_roles_list)
    return len(paths)
