# Mayker Order Tool

A group food-ordering web app for a single, preselected restaurant. An admin enters the restaurant's menu, generates a shareable link, and distributes it to their team. Team members open the link, select menu items, and see a running subtotal of their own selections. When everyone is done, the admin closes the order and exports a consolidated list for manual submission to Deliveroo.

## Quick Start

```bash
cp .env.example .env
docker compose up
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs (Swagger): http://localhost:8000/docs

## Prerequisites

- Docker 24+

## Configuration

Copy `.env.example` to `.env` and adjust as needed:

| Variable | Default | Description |
|---|---|---|
| `RESTAURANT_NAME` | `Trattoria Demo` | Restaurant name shown in the UI |
| `BACKEND_PORT` | `8000` | Host port for the backend API |
| `FRONTEND_PORT` | `5173` | Host port for the frontend |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed CORS origins for the backend |

## Repository structure

```
.
├── backend/          # FastAPI Python backend
├── frontend/         # React + Vite + Tailwind frontend
├── e2e/              # Playwright end-to-end tests
├── docker-compose.yml
└── docs/DEVELOPMENT.md
```

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for full development instructions, including how to run unit, integration, and E2E tests without Docker.

---

### Required MCP connections

This project uses a Claude Code-driven delivery framework. Two MCP connections are required:

- **Issue tracker** (ClickUp) for reading features and updating status
- **Git provider** (GitHub) for PRs and review comments

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for setup instructions.
