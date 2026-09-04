# Secure and Autonomous Multi-Agent Enterprise Assistant

Implements FR-1 (see [REQUIREMENTS.md](REQUIREMENTS.md)): authenticated users submit natural-language enterprise
requests via the frontend, which the backend accepts and persists. Later FRs (orchestration, RAG, RBAC, XAI, HITL)
build on this foundation.

## Stack

- **Backend:** FastAPI + SQLAlchemy + Postgres, JWT auth (`backend/`)
- **Frontend:** React + Vite (`frontend/`)
- **Database:** Postgres, run via Docker Compose

## Architecture

`backend/app/` separates concerns into independently-developable/testable packages (NFR-9):

- **`agents/`** — one file per specialized agent (`rag_agent.py`, `security_agent.py`, `analytics_agent.py`,
  `workflow_agent.py`, `validation_agent.py`), each implementing `BaseAgent.run()`. `registry.py` is the single
  place a new agent gets wired in (see its module docstring).
- **`orchestrator/`** — routes a request to agent(s) (`decomposer.py`) and runs the dispatch loop
  (`orchestrator.py`). Deliberately agent-agnostic: it doesn't know what "rag" or "workflow" mean, only that it
  has an `AgentResult` back from whichever agent ran.
- **`rbac/`** — role/permission checks (`roles.py`: `can_use_agent`, `require_admin`) and continuous identity
  re-verification (`zero_trust.py`).
- **`hitl/`** — the human-in-the-loop approval gate (`gate.py`: `requires_approval`).
- **`audit/`** — the append-only audit log writer (`logger.py`).
- **`rag/`** — retrieval pipeline, embeddings, vector store client, LLM client.
- **`workflow/`** — simulated enterprise functions and keyword-based step planning.
- **`api/routes/`** — FastAPI route handlers; thin, delegate to the packages above rather than reimplementing
  their logic.
- **`models/` / `schemas/`** — SQLAlchemy ORM models vs. Pydantic request/response shapes, kept distinct.
- **`core/`** — config (`config.py`, all settings loaded through one `Settings` object), DB engine/session,
  password/JWT helpers.

`frontend/src/` separates API calls (`api/*.js`, one file per resource) from presentation (`pages/*.jsx`) —
pages import named functions rather than calling `axios`/`fetch` directly.

### Running tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

Tests run against an in-memory SQLite DB (see `tests/conftest.py`) — no Docker/Postgres/Ollama required, so the
security/orchestration/agent-selection logic in `rbac/`, `hitl/`, `orchestrator/`, and `agents/registry.py` can be
verified in isolation.

## Prerequisites

- Python 3.11+ (tested with 3.12)
- Node.js 20+
- Docker (for Postgres)

## Setup

### 1. Database

```bash
docker compose up -d postgres
```

Postgres is exposed on host port **5439** (not 5432, to avoid clashing with other local Postgres instances) —
see `docker-compose.yml`.

### 2. Backend

Windows (PowerShell):

```powershell
cd backend
python -m venv .venv
./.venv/Scripts/pip install -r requirements.txt

cp .env.example .env   # defaults already point at the Docker Postgres above
./.venv/Scripts/python -m uvicorn app.main:app --reload --port 8123
```

Linux/macOS:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # defaults already point at the Docker Postgres above
python -m uvicorn app.main:app --reload --port 8123
```

API docs: http://localhost:8123/docs

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_URL defaults to http://localhost:8123
npm run dev
```

App: http://localhost:5173

## FR-1 flow

1. Register at `/register`, or sign in at `/login` if you already have an account.
2. On the `/requests` page, type a natural-language request (e.g. "Generate this month's headcount report for
   Engineering") and submit it.
3. The backend persists it as an `EnterpriseRequest` row with `status: "received"` and the UI lists it immediately.
4. Visiting `/requests` while logged out redirects to `/login` — requests are only accepted from authenticated
   users (`POST /api/requests` returns 401 without a bearer token).

No orchestration/agent dispatch happens yet — that's FR-2 and later.

## Notes

- `Base.metadata.create_all()` runs on backend startup instead of migrations, since the schema is still small.
  Introduce Alembic once models stabilize.
- `role` on `User` defaults to `"employee"` but isn't enforced anywhere yet — that's FR-4 (RBAC).
