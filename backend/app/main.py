import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import approvals, auth, requests
from app.core.config import settings
from app.core.database import Base, engine
from app.models import (  # noqa: F401 -- register models with Base
    AuditLog,
    EnterpriseRequest,
    SubTask,
    User,
    WorkflowExecution,
)
from app.rag.ingest import ingest_documents

logger = logging.getLogger(__name__)

app = FastAPI(title="Secure Autonomous Multi-Agent Enterprise Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(requests.router)
app.include_router(approvals.router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)

    try:
        count = ingest_documents()
        logger.info("RAG knowledge base ready: %d document(s) ingested.", count)
    except Exception:
        logger.exception(
            "Could not ingest RAG documents on startup (is the chromadb service running?). "
            "The app will still start; the RAG agent will report errors until this is fixed."
        )


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
