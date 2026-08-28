# Secure and Autonomous Multi-Agent Enterprise Assistant

Implements FR-1 (see [REQUIREMENTS.md](REQUIREMENTS.md)): authenticated users submit natural-language enterprise
requests via the frontend, which the backend accepts and persists. Later FRs (orchestration, RAG, RBAC, XAI, HITL)
build on this foundation.

## Stack

- **Backend:** FastAPI + SQLAlchemy + Postgres, JWT auth (`backend/`)
- **Frontend:** React + Vite (`frontend/`)
- **Database:** Postgres, run via Docker Compose

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

```bash
cd backend
python -m venv .venv
./.venv/Scripts/pip install -r requirements.txt   # Windows
# source .venv/bin/activate && pip install -r requirements.txt   # Linux/macOS

cp .env.example .env   # defaults already point at the Docker Postgres above
./.venv/Scripts/python -m uvicorn app.main:app --reload --port 8123
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
