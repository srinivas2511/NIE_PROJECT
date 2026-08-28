from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, requests
from app.core.config import settings
from app.core.database import Base, engine
from app.models import EnterpriseRequest, User  # noqa: F401 -- register models with Base

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


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
