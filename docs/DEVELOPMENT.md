# Development Guide — Mayker Order Tool

## Prerequisites

- **Docker 24+** and Docker Compose (for running the full stack)
- **Node.js 20+** (for frontend development and E2E tests)
- **Python 3.12+** with `uv` or `pip` (for backend development)
- **PostgreSQL 16** (automatically provided by Docker Compose)

---

## Running the full stack

```bash
cp .env.example .env
docker compose up
```

Services:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs (Swagger): http://localhost:8000/docs

---

## Backend development

### Setup

```bash
cd backend
uv venv .venv --python 3.13    # or python3.12 -m venv .venv
source .venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
```

### Running the backend locally

You need a running Postgres instance (e.g. via `docker compose up postgres`).

```bash
export DATABASE_URL=postgresql+asyncpg://ordertool:ordertool@localhost:5432/ordertool
cd backend
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Running unit tests

Unit tests do not require Postgres — they mock the database session.

```bash
cd backend
source .venv/bin/activate
export DATABASE_URL=postgresql+asyncpg://placeholder:placeholder@localhost/placeholder
python -m pytest tests/unit/ -v
```

### Running integration tests

Integration tests require a running Postgres instance.

```bash
export DATABASE_URL=postgresql+asyncpg://ordertool:ordertool@localhost:5432/ordertool
export TEST_DATABASE_URL=postgresql+asyncpg://ordertool:ordertool@localhost:5432/ordertool_test
cd backend
python -m pytest tests/integration/ -v
```

> Integration tests use the `TEST_DATABASE_URL` env var when set, falling back to `DATABASE_URL`. They run Alembic migrations and roll back after each test module.

### Running all backend tests with coverage

```bash
cd backend
python -m pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## Frontend development

### Setup

```bash
cd frontend
npm install
```

### Running the frontend dev server

The frontend requires the backend to be running (directly or via Docker Compose).

```bash
cd frontend
cp .env.example .env     # VITE_API_URL=http://localhost:8000
npm run dev              # http://localhost:5173
```

### TypeScript check

```bash
cd frontend
npm run lint
```

### Building for production

```bash
cd frontend
npm run build
```

---

## E2E tests (Playwright)

E2E tests require the **full stack** (frontend preview build + backend + Postgres) to be running.

### Setup

```bash
cd e2e
npm install
npx playwright install chromium
```

### Running E2E tests

With the full stack running via `docker compose up`:

```bash
cd e2e
BASE_URL=http://localhost:5173 npm test
```

Or let Playwright start the frontend preview automatically (backend must be available at `http://localhost:8000`):

```bash
cd e2e
npm test
```

---

## Project structure

```
.
├── backend/
│   ├── app/
│   │   ├── core/           # Config, logging, exceptions
│   │   ├── db/             # SQLAlchemy engine, session, base
│   │   ├── models/         # ORM models (Order, MenuItem)
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── repositories/   # Database access layer
│   │   ├── services/       # Business logic layer
│   │   ├── routers/        # FastAPI route handlers
│   │   └── main.py         # App factory
│   ├── alembic/            # Database migrations
│   ├── tests/
│   │   ├── unit/           # Unit tests (mock DB)
│   │   └── integration/    # Integration tests (real DB)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/            # API client and type definitions
│   │   ├── components/     # React components
│   │   ├── config/         # Constants and configuration
│   │   ├── hooks/          # Custom React hooks
│   │   ├── icons/          # Lucide icon re-exports
│   │   ├── lib/            # Utility functions (cn, etc.)
│   │   ├── pages/          # Page-level components
│   │   └── ui/             # Atomic UI components
│   └── package.json
├── e2e/
│   ├── tests/              # Playwright E2E test specs
│   └── uat/                # UAT Gherkin features + manual scripts
└── docker-compose.yml
```

---

## MCP connections

See [../README.md](../README.md) and the project's `CLAUDE.md` for MCP setup instructions.

## AI delivery framework

This project uses the `claude-dev` plugin. Commands:

| Command | Purpose |
|---|---|
| `/claude-dev:plan-feature {ID}` | Generate an architect plan |
| `/claude-dev:build-feature {ID}` | Implement from an approved plan |
| `/claude-dev:revise-feature {ID}` | Apply PR review feedback |
| `/claude-dev:refactor {scope}` | Code quality improvements |
