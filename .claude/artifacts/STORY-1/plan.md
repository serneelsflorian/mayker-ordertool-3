# Implementation Plan, STORY-1: Admin starts a group order and enters the menu

## Feature
> As an admin, I want to start a group order for the preselected restaurant and enter its menu items, so the team has an accurate list to order from.
>
> - On app load with no active order, the admin sees the preselected restaurant name displayed (hardcoded, not editable) and an empty menu-entry form.
> - The admin can add a menu item by entering a name (required, text); price is OPTIONAL (when provided, must be a positive number with up to 2 decimals); category is an optional text field.
> - Attempting to add an item with an empty name shows an inline error and does not add the item. A price left empty is allowed; only a non-numeric or negative price (when something is entered) shows an inline error and blocks adding.
> - Each added item appears immediately in a list below the form, showing name, price if provided, and category if provided.
> - The admin can remove any item from the list before sharing; removal updates the list immediately.
> - The admin cannot proceed to generate a link until at least one valid menu item exists; the generate-link action is disabled until then.

## Acceptance Criteria
- [ ] AC1 — On app load with no active order, the admin sees the preselected (hardcoded, non-editable) restaurant name and an empty menu-entry form.
- [ ] AC2 — The admin can add a menu item with name (required, text), price (OPTIONAL; when provided must be a positive number, up to 2 decimals), and category (optional, text).
- [ ] AC3 — Adding with an empty name shows an inline error and does not add the item. An empty price is allowed; only a non-numeric or negative price (when a value is entered) shows an inline error and blocks adding.
- [ ] AC4 — Each added item appears immediately in a list below the form, showing name, price (if provided), and category (if provided).
- [ ] AC5 — The admin can remove any item from the list before sharing; removal updates the list immediately.
- [ ] AC6 — The admin cannot proceed to generate a link until at least one valid menu item exists; the generate-link action is disabled until then.

## Plan Overview

STORY-1 is the **scaffold feature**: it lays down the full `backend/` (FastAPI + SQLAlchemy 2.x async + Pydantic v2 + Alembic), `frontend/` (Vite + React + TypeScript + Tailwind + React Router), and `e2e/` (Playwright) project structure, Docker Compose wiring (frontend + backend + Postgres 16), and shared test infrastructure, then implements the menu-setup flow on top of it.

The feature itself does two things:

1. **Start a group order** — on app load with no active order, the frontend creates a new server-side order record (status `open`) and navigates the admin to `/order/:id`. The order and its menu items are persisted in Postgres (per CLAUDE.md fixed decision #1 — **never** localStorage/sessionStorage). This makes the order shareable, refresh-safe, and cross-browser, and gives STORY-2 an existing order id to surface as a link.
2. **Enter the menu** — the admin adds menu items (name required; price optional; category optional) which are persisted via the backend; they render in a list below the form; the admin can remove items; the "Generate share link" affordance is disabled until at least one menu item exists.

Layers exercised:
- **Backend:** Router → Service → Repository → Schemas (DTOs) → Models, with the transactional boundary in the service layer, custom `AppException` hierarchy, global FastAPI exception handlers, and structured logging (CLAUDE.md fixed decision #6).
- **Frontend:** React Router route `/order/:id` plus a root bootstrap route, a typed API client module, shadcn-style UI atoms, and the Menu-Setup page reimplemented from scratch using the prototype's visual patterns only.

### Key architecture decisions (documented, do NOT re-derive)

**A. Server-persisted order on "start a group order" (chosen).** STORY-1 creates the order record server-side and persists menu items to Postgres via the backend. This directly satisfies CLAUDE.md fixed decision #1 (shared, server-persisted state keyed by `/order/:id`, survives refresh, works across browsers/sessions). A client-held-menu alternative (keeping the menu only in React state until STORY-2) is **rejected**: it would not persist, would lose the menu on refresh, and would force STORY-2 to retrofit persistence — a direct violation of fixed decision #1.

**B. Landing on a fresh order ("on app load with no active order").** The frontend uses a **root bootstrap route** (`/`): when the admin opens the app with no order id in the URL, a small bootstrap component calls `POST /api/orders` to create a fresh `open` order, then redirects (`navigate(\`/order/${id}\`, { replace: true })`) to the canonical `/order/:id` route. All real menu work happens on `/order/:id`, which reads order state via `GET /api/orders/{id}`. This keeps a single source of truth (the server), makes the URL shareable immediately (foundation for STORY-2), and means a refresh of `/order/:id` re-fetches from Postgres rather than re-creating an order. Rationale: chosen over "create an order only when the first item is added" because the first AC explicitly says the admin sees the restaurant name and an empty form on load, and decision #1 requires the id to live in the URL.

**C. Price is OPTIONAL — this is a foundational contract decision.** Per the STORY-1 acceptance criteria, price is optional: an empty price is allowed and the item is added with no price. Only a non-empty, non-numeric, or non-positive price blocks adding. This is enforced on **both** the client (inline validation) and the server (Pydantic v2 validation). Price is stored as a **nullable** `NUMERIC(10,2)` column. See **CRITICAL divergence from the prototype** below — the builder must NOT copy the prototype's required-price validation. Later stories (STORY-2..7) read against this nullable-price contract.

**D. Restaurant is hardcoded.** The restaurant name is a backend config constant (`settings.restaurant_name`, default e.g. `"Trattoria Demo"`, overridable via `RESTAURANT_NAME` env var) returned in the order read response, and a frontend display constant fed from the API response. No restaurant DB table, no restaurant CRUD (CLAUDE.md fixed decision #5).

### CRITICAL divergence from the design prototype (builder MUST follow the AC, not the prototype)

`docs/prototype/src/app/App.tsx` lines ~354–360 validate price as **required and positive**:
```ts
const p = Number(price);
if (!price.trim() || isNaN(p) || p <= 0) e.price = "Enter a positive number";
```
**This is wrong for STORY-1.** The acceptance criteria make price **OPTIONAL**. The builder must implement:
- Empty/blank price → **allowed**, item added with `price = null`.
- Non-empty price that is non-numeric OR ≤ 0 → inline error, blocks add.
- Non-empty valid price → rounded/validated to ≤ 2 decimals, stored as `NUMERIC(10,2)`.

Additionally, the prototype uses seed data, in-memory React state, `localStorage`-free client-only state, and **no backend**. **Do NOT carry any of that over.** STORY-1 persists everything server-side. The prototype is a **visual reference only** (per coding_standards.md §3.4 — reimplement from scratch).

## Infrastructure Scaffolding (scaffold feature)

The following infrastructure will be created alongside the feature.

### Project Structure

```
backend/
  app/
    __init__.py
    main.py                         # FastAPI app factory; mounts routers; registers exception handlers; entrypoint app.main:app
    core/
      __init__.py
      config.py                     # Pydantic-settings: DATABASE_URL, RESTAURANT_NAME, CORS origins
      logging.py                    # logging config (NEVER print)
      exceptions.py                 # AppException base + NotFoundError + ValidationError subclasses
      exception_handlers.py         # global FastAPI handlers → consistent JSON error shape
    db/
      __init__.py
      base.py                       # DeclarativeBase
      session.py                    # async engine + async_sessionmaker + get_db dependency
    models/
      __init__.py
      order.py                      # Order ORM model
      menu_item.py                  # MenuItem ORM model
    schemas/
      __init__.py
      order.py                      # OrderCreateResponse, OrderRead DTOs
      menu_item.py                  # MenuItemCreate, MenuItemRead DTOs
    repositories/
      __init__.py
      order_repository.py           # OrderRepository
      menu_item_repository.py       # MenuItemRepository
    services/
      __init__.py
      order_service.py              # OrderService (transactional boundary)
      menu_item_service.py          # MenuItemService (transactional boundary)
    routers/
      __init__.py
      orders.py                     # /api/orders, /api/orders/{id}
      menu_items.py                 # /api/orders/{id}/menu-items[...]
  tests/
    __init__.py
    conftest.py                     # module-scoped Postgres fixture, session-scoped httpx async client, migration runner, per-test rollback
    unit/
      __init__.py
    integration/
      __init__.py
  alembic/
    env.py                          # async Alembic env
    script.py.mako
    versions/
      0001_create_orders_and_menu_items.py
  alembic.ini
  requirements.txt                  # MUST be at backend/requirements.txt (CI: pip install -r requirements.txt)
  Dockerfile
  .env.example
frontend/
  src/
    main.tsx                        # React entry; mounts RouterProvider
    App.tsx                         # Router definition (root bootstrap + /order/:id)
    index.css                       # Tailwind directives
    config/
      constants.ts                  # API base URL helper, i18n-ready text constants
    lib/
      utils.ts                      # cn() class-merge helper (shadcn-style)
    api/
      client.ts                     # fetch wrapper: base URL, JSON, error mapping, typed errors
      orders.ts                     # typed order API functions
      types.ts                      # OrderRead, MenuItem, MenuItemCreate request/response types
    ui/                             # shadcn-style atoms (reimplemented from scratch)
      button.tsx
      input.tsx
      label.tsx
      card.tsx
      badge.tsx
      separator.tsx
    icons/
      index.ts                      # re-exports lucide-react icons (Plus, Trash2, Link) — no inline <svg> in feature files
    components/
      TopBar.tsx                    # restaurant logo mark + name + "Group order · Open" status line
      MenuItemForm.tsx              # name/price/category inputs + Add button + inline errors
      MenuItemList.tsx              # list of added items (name, optional Badge category, optional price, remove)
      MenuItemRow.tsx               # single item row with remove button
      EmptyState.tsx                # dashed empty-state box
      GenerateLinkSection.tsx       # disabled-until-≥1-item "Generate share link" affordance + helper text
    pages/
      OrderBootstrap.tsx            # root route: create order, redirect to /order/:id
      OrderSetupPage.tsx            # /order/:id admin menu-setup screen (composes the components above)
    hooks/
      useOrder.ts                   # load order + add/remove menu item state, calls api/orders
  index.html
  package.json
  package-lock.json                 # MUST exist at frontend/package-lock.json (CI: npm ci with cache-dependency-path)
  tsconfig.json
  tsconfig.node.json
  vite.config.ts                    # dev server + preview configured on port 5173
  tailwind.config.ts                # brand colors (teal/coral/bluegrey/taupe/bg-soft)
  postcss.config.js
  Dockerfile
  .env.example
e2e/
  package.json
  package-lock.json
  playwright.config.ts              # baseURL from BASE_URL env, screenshot-on-failure, webServer optional
  tests/
    menu-setup.spec.ts              # STORY-1 E2E specs
  uat/
    STORY-1.feature                 # Gherkin (UAT OPTIONAL per CLAUDE.md)
    STORY-1-manual-uat.md           # manual UAT script
docker-compose.yml                  # frontend + backend + postgres:16
.env.example                        # root: DATABASE_URL, RESTAURANT_NAME, ports
```

### Docker Setup
- `backend/Dockerfile` — Python 3.12-slim, install `requirements.txt`, run `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- `frontend/Dockerfile` — Node 20, `npm ci`, `npm run build`, serve via `vite preview --host --port 5173` (dev compose may use `npm run dev -- --host --port 5173`).
- `docker-compose.yml` (root) — three services:
  - `postgres` (image `postgres:16`, env `POSTGRES_USER=ordertool`, `POSTGRES_PASSWORD=ordertool`, `POSTGRES_DB=ordertool`, volume for data, port `5432`).
  - `backend` (build `./backend`, depends_on postgres healthy, env `DATABASE_URL=postgresql+asyncpg://ordertool:ordertool@postgres:5432/ordertool`, `RESTAURANT_NAME`, port `8000`; runs Alembic migrations on start then uvicorn).
  - `frontend` (build `./frontend`, env `VITE_API_URL` pointing at backend, port `5173`).
- `.env.example` (root) and per-service `.env.example`: `DATABASE_URL`, `RESTAURANT_NAME`, `BACKEND_PORT=8000`, `FRONTEND_PORT=5173`, `VITE_API_URL=http://localhost:8000`, `CORS_ORIGINS=http://localhost:5173`.

### Test Infrastructure
- **Shared backend test config:** `backend/tests/conftest.py` per coding_standards §2.5 / testing_standards §1.2:
  - Module-scoped real Postgres instance fixture (reads `DATABASE_URL`; in CI this points at the `postgres:16` service `ordertool_test` DB — do NOT hardcode connection strings, read from env per testing_standards §1.5/anti-patterns).
  - Migration runner fixture that applies the Alembic migration (or `Base.metadata.create_all`) against the test DB before tests.
  - Session-scoped httpx async test client fixture using `ASGITransport(app=app)` (no real network).
  - Per-test isolation via a transaction rolled back after each test (nested transaction / savepoint pattern), so tests do not depend on order.
- **Test directories** (from CLAUDE.md): unit → `backend/tests/unit/`; integration → `backend/tests/integration/`.
- **E2E framework config:** `e2e/playwright.config.ts` — `baseURL` from `BASE_URL` env (`http://localhost:5173`), `API_URL` from env for setup seeding, `screenshot: 'only-on-failure'`, retries off locally, projects = chromium. Tests in `e2e/tests/`.
- **UAT directory:** `e2e/uat/` (Gherkin `.feature` + manual script). UAT is OPTIONAL per CLAUDE.md; included as a thin artifact, not wired to a BDD runner.

### CI Pipeline Configuration
CI already exists at `.github/workflows/ci.yml` (generated by `/init-project`). **Do NOT rewrite it.** The scaffold MUST conform to its assumptions. Verified alignment requirements (builder must satisfy all):

| CI expectation | Scaffold must provide |
|---|---|
| `backend-unit`: `working-directory: backend`, `pip install -r requirements.txt`, `pytest tests/unit/ -v --cov=app --cov-report=xml --cov-fail-under=80` | `backend/requirements.txt`; package `backend/app/`; tests under `backend/tests/unit/`; ≥80% coverage on service-layer logic. |
| `backend-integration`: postgres:16 service, `DATABASE_URL=postgresql+asyncpg://ordertool:ordertool@localhost:5432/ordertool_test`, `pytest tests/integration/ -v` | conftest reads `DATABASE_URL` from env; integration tests under `backend/tests/integration/`; migration runner creates schema in `ordertool_test`. |
| `e2e`: `npm ci` in `frontend` (needs `frontend/package-lock.json`), `npx playwright install --with-deps` in `e2e`, `npm run build` in `frontend`, `uvicorn app.main:app` on :8000, `npx playwright test` in `e2e` with `BASE_URL=http://localhost:5173`, `API_URL=http://localhost:8000` | entrypoint `app.main:app`; `frontend/package-lock.json` committed; `e2e/package.json` with `@playwright/test`; `e2e/package-lock.json`; Playwright config reads `BASE_URL`. |
| `mark-done`: parses `feature/STORY-\d+` from branch | branch is `feature/STORY-1-admin-starts-group-order` (already set). |

**GAP to document for the builder:** the CI `e2e` job builds the frontend (`npm run build`) and starts only the backend on `:8000`, but Playwright's `BASE_URL` is `http://localhost:5173`. Nothing in CI currently serves the built frontend on `:5173`. The scaffold must close this by having `e2e/playwright.config.ts` start the frontend on `:5173` via a Playwright `webServer` block (e.g. `command: 'npm run preview -- --port 5173'` with `cwd: '../frontend'`, `url: 'http://localhost:5173'`, `reuseExistingServer: !process.env.CI`). This serves the Vite preview build on 5173 without editing CI. Document this clearly; do not edit `ci.yml`.

## Frontend Plan

- **Components to create:**
  - `frontend/src/ui/{button,input,label,card,badge,separator}.tsx` — shadcn-style atoms, reimplemented from scratch (Tailwind utility classes, `cn()` helper), one component per file.
  - `frontend/src/icons/index.ts` — re-export `Plus`, `Trash2`, `Link` (and `ShoppingBag` for the TopBar mark) from `lucide-react`; feature files import from here (no inline `<svg>`, coding_standards §3.5).
  - `frontend/src/components/TopBar.tsx` — header with teal logo mark + restaurant name + `Group order · Open` status line.
  - `frontend/src/components/MenuItemForm.tsx` — responsive grid `sm:grid-cols-[2fr_1fr_1fr_auto] sm:items-end`: Item name / Price / Category / Add button; inline coral error text under name and price; client-side validation matching the OPTIONAL-price contract.
  - `frontend/src/components/MenuItemList.tsx` + `MenuItemRow.tsx` — list below the form; each row shows name, optional category `Badge`, optional price (only when present), and a ghost trash icon button with `aria-label`.
  - `frontend/src/components/EmptyState.tsx` — dashed box "No menu items yet. Add your first item above."
  - `frontend/src/components/GenerateLinkSection.tsx` — "Generate share link" button **disabled until ≥1 menu item exists**, with helper text "Add at least one menu item first." when disabled. STORY-1 builds ONLY the disabled/enabled affordance + gating — **no actual link generation** (that is STORY-2; no gold plating).
  - `frontend/src/pages/OrderBootstrap.tsx` — root route component: on mount calls `POST /api/orders`, then `navigate('/order/' + id, { replace: true })`.
  - `frontend/src/pages/OrderSetupPage.tsx` — `/order/:id` page: loads order via `GET /api/orders/{id}`, composes TopBar + MenuItemForm + MenuItemList + GenerateLinkSection.
  - `frontend/src/hooks/useOrder.ts` — encapsulates load + add + remove against the API client; returns `{ order, menuItems, addItem, removeItem, loading, error }`.
- **Routes (React Router):**
  - `/` → `OrderBootstrap` (creates order, redirects).
  - `/order/:id` → `OrderSetupPage`.
- **State management:** Local React state + the `useOrder` hook (native hooks per coding_standards §3.3). The **server is the source of truth**; the menu list state is hydrated from `GET /api/orders/{id}` and updated optimistically/after each add/remove API call. **No localStorage/sessionStorage** for order state (fixed decision #1).
- **Design reference notes (visual only, reimplemented from scratch):**
  - Brand colors defined in `tailwind.config.ts` (NOT a `<style>` block like the prototype): teal `#269A91` (primary; hover `#1f857d`), coral `#D44858` (destructive/errors; hover `#b93b48`), bluegrey `#9ABFCB`, taupe `#A39286`, soft bg `#F6F4F1`.
  - Card-based layout (CardHeader/CardTitle/CardContent), max-width container `max-w-5xl mx-auto p-4 sm:p-6`, mobile-first.
  - Inline errors in coral under the relevant field; remove button is a ghost trash icon.
  - `data-testid` on all interactive elements / key containers (coding_standards §3.6), format `{component}-{element}`, suffix `-{id}` on repeated rows. Semantic HTML + `aria-label` on icon buttons (§3.2).

## Backend Plan

- **Endpoints** (all under `/api`):
  - `POST /api/orders` — create a new order (status `open`); returns `{ id, status, restaurant_name }`. (Used by the root bootstrap route.)
  - `GET /api/orders/{id}` — read an order with its menu items; returns order + `menu_items[]`. 404 if not found. (Used on `/order/:id` load + refresh.)
  - `POST /api/orders/{id}/menu-items` — add a menu item (`name` required; `price` optional/nullable; `category` optional); returns the created item. 404 if order missing, 422 on validation failure.
  - `DELETE /api/orders/{id}/menu-items/{item_id}` — remove a menu item; 204 on success; 404 if order or item missing.
- **Service layer** (`order_service.py`, `menu_item_service.py`):
  - `OrderService.create_order()` — create `Order(status="open")`, commit, return.
  - `OrderService.get_order(id)` — fetch order + items eagerly; raise `NotFoundError` if absent.
  - `MenuItemService.add_item(order_id, payload)` — verify order exists (`NotFoundError` if not), construct `MenuItem`, persist, commit, return. Business validation: name non-empty after trim; price (if present) positive and quantized to 2 decimals.
  - `MenuItemService.remove_item(order_id, item_id)` — verify item belongs to order; delete; commit; `NotFoundError` if missing.
  - **Transactional boundary lives here** (coding_standards §2.2): the service opens/commits/rolls back the unit of work; the repository only issues queries.
- **Repository layer** (`order_repository.py`, `menu_item_repository.py`): thin async SQLAlchemy 2.x query methods — `add`, `get_by_id` (with `selectinload(Order.menu_items)`), `add_item`, `get_item`, `delete_item`. No business logic.
- **Schemas (DTOs)** kept separate from ORM models (`schemas/order.py`, `schemas/menu_item.py`):
  - `OrderCreateResponse { id: str(UUID), status: Literal["open","closed"], restaurant_name: str }`
  - `OrderRead { id, status, restaurant_name, menu_items: list[MenuItemRead] }`
  - `MenuItemCreate { name: str (min_length 1 after strip), price: Decimal | None (gt 0, max 2 decimals), category: str | None }`
  - `MenuItemRead { id, name, price: Decimal | None, category: str | None }`
  - Pydantic v2 validators: `name` must be non-blank; `price` validated only when not null (positive, ≤2 decimals).
- **Models (ORM, SQLAlchemy 2.x async, `Mapped`/`mapped_column`):**
  - `Order`: `id` (UUID PK, server default), `status` (str/enum, default `"open"`), `created_at`, `updated_at` (timestamptz, server defaults), relationship `menu_items` (cascade delete-orphan).
  - `MenuItem`: `id` (UUID PK), `order_id` (FK → orders.id, indexed, ON DELETE CASCADE), `name` (str, not null), `price` (`Numeric(10,2)`, **nullable**), `category` (str, nullable), `created_at`, `updated_at`.
  - Restaurant name is a **config constant**, not a table.
- **Error handling:** custom `AppException` base in `core/exceptions.py` with `NotFoundError` (→404) and `ValidationError` (→422) subclasses; global handlers in `core/exception_handlers.py` return the consistent JSON error shape (see API Contract). Pydantic request-validation errors are also mapped to the same 422 shape. Structured logging via `core/logging.py` — never `print()`.
- **Migrations:** Alembic configured with the async engine (`alembic/env.py` using `DATABASE_URL`). Migration `0001_create_orders_and_menu_items` creates `orders` and `menu_items` tables (with FK + cascade + indexes + nullable price). Alembic tooling is part of the scaffold.

## API Integration Plan
No external API integration.

## API Contract

Base path: `/api`. All requests/responses are JSON. IDs are UUID strings. Price is a decimal string or `null`.

### 1. Create order
- **Method:** `POST`
- **URL:** `/api/orders`
- **Request:** (no body required)
```json
{}
```
- **Response 201:**
```json
{
  "id": "8f1c2e6a-3b4d-4e5f-9a1b-2c3d4e5f6a7b",
  "status": "open",
  "restaurant_name": "Trattoria Demo"
}
```

### 2. Read order (with menu items)
- **Method:** `GET`
- **URL:** `/api/orders/{id}`
- **Response 200:**
```json
{
  "id": "8f1c2e6a-3b4d-4e5f-9a1b-2c3d4e5f6a7b",
  "status": "open",
  "restaurant_name": "Trattoria Demo",
  "menu_items": [
    { "id": "a1...", "name": "Margherita", "price": "9.50", "category": "Pizza" },
    { "id": "b2...", "name": "Tap Water",  "price": null,   "category": null }
  ]
}
```
- **Response 404 (order not found):**
```json
{ "error": { "code": "not_found", "message": "Order 8f1c2e6a-... not found" } }
```

### 3. Add menu item
- **Method:** `POST`
- **URL:** `/api/orders/{id}/menu-items`
- **Request (price provided):**
```json
{ "name": "Margherita", "price": "9.50", "category": "Pizza" }
```
- **Request (price omitted — VALID, price is optional):**
```json
{ "name": "Tap Water", "category": null }
```
- **Response 201:**
```json
{ "id": "a1b2c3d4-...", "name": "Margherita", "price": "9.50", "category": "Pizza" }
```
- **Response 422 (empty name):**
```json
{ "error": { "code": "validation_error", "message": "Validation failed", "details": [ { "field": "name", "message": "Name is required" } ] } }
```
- **Response 422 (non-numeric or non-positive price when a value was entered):**
```json
{ "error": { "code": "validation_error", "message": "Validation failed", "details": [ { "field": "price", "message": "Price must be a positive number with up to 2 decimals" } ] } }
```
- **Response 404 (order not found):**
```json
{ "error": { "code": "not_found", "message": "Order 8f1c2e6a-... not found" } }
```

### 4. Remove menu item
- **Method:** `DELETE`
- **URL:** `/api/orders/{id}/menu-items/{item_id}`
- **Response 204:** (no body)
- **Response 404 (order or item not found):**
```json
{ "error": { "code": "not_found", "message": "Menu item a1b2c3d4-... not found in order 8f1c2e6a-..." } }
```

**Global error shape** (all `AppException`-derived errors and request-validation errors):
```json
{ "error": { "code": "<machine_code>", "message": "<human message>", "details": [ /* optional field errors */ ] } }
```

## File Manifest

### New files

**Backend**
- `backend/requirements.txt`: pinned deps — fastapi, uvicorn[standard], sqlalchemy[asyncio]>=2, asyncpg, pydantic>=2, pydantic-settings, alembic, pytest, pytest-asyncio, pytest-cov, httpx.
- `backend/Dockerfile`: Python 3.12-slim image; install reqs; run uvicorn `app.main:app`.
- `backend/.env.example`: `DATABASE_URL`, `RESTAURANT_NAME`, `CORS_ORIGINS`.
- `backend/alembic.ini`: Alembic config.
- `backend/alembic/env.py`: async Alembic env reading `DATABASE_URL`.
- `backend/alembic/script.py.mako`: migration template.
- `backend/alembic/versions/0001_create_orders_and_menu_items.py`: creates `orders` + `menu_items` tables (nullable `price NUMERIC(10,2)`, FK cascade, indexes).
- `backend/app/__init__.py`
- `backend/app/main.py`: app factory; mounts routers; registers exception handlers; CORS; `app` = entrypoint for `app.main:app`.
- `backend/app/core/__init__.py`
- `backend/app/core/config.py`: pydantic-settings `Settings` (DATABASE_URL, RESTAURANT_NAME default "Trattoria Demo", CORS_ORIGINS).
- `backend/app/core/logging.py`: logging configuration helper.
- `backend/app/core/exceptions.py`: `AppException`, `NotFoundError`, `ValidationError`.
- `backend/app/core/exception_handlers.py`: global handlers → consistent JSON error shape; maps Pydantic validation errors.
- `backend/app/db/__init__.py`
- `backend/app/db/base.py`: `DeclarativeBase`.
- `backend/app/db/session.py`: async engine, `async_sessionmaker`, `get_db` dependency.
- `backend/app/models/__init__.py`
- `backend/app/models/order.py`: `Order` ORM model.
- `backend/app/models/menu_item.py`: `MenuItem` ORM model.
- `backend/app/schemas/__init__.py`
- `backend/app/schemas/order.py`: `OrderCreateResponse`, `OrderRead`.
- `backend/app/schemas/menu_item.py`: `MenuItemCreate`, `MenuItemRead` (price optional/nullable validation).
- `backend/app/repositories/__init__.py`
- `backend/app/repositories/order_repository.py`: `OrderRepository`.
- `backend/app/repositories/menu_item_repository.py`: `MenuItemRepository`.
- `backend/app/services/__init__.py`
- `backend/app/services/order_service.py`: `OrderService` (transactional boundary).
- `backend/app/services/menu_item_service.py`: `MenuItemService` (transactional boundary).
- `backend/app/routers/__init__.py`
- `backend/app/routers/orders.py`: `POST /api/orders`, `GET /api/orders/{id}`.
- `backend/app/routers/menu_items.py`: `POST` / `DELETE` menu-item endpoints.
- `backend/tests/__init__.py`
- `backend/tests/conftest.py`: Postgres fixture + httpx async client + migration runner + per-test rollback.
- `backend/tests/unit/__init__.py`
- `backend/tests/unit/test_menu_item_service.py`: unit tests for MenuItemService (incl. optional-price rules).
- `backend/tests/unit/test_order_service.py`: unit tests for OrderService.
- `backend/tests/unit/test_menu_item_schema.py`: Pydantic validation unit tests (optional price, blank name).
- `backend/tests/integration/__init__.py`
- `backend/tests/integration/test_orders_api.py`: router/repo integration (create, read, 404).
- `backend/tests/integration/test_menu_items_api.py`: router/repo integration (add with/without price, remove, 422, 404).

**Frontend**
- `frontend/package.json`: react, react-dom, react-router-dom, lucide-react, tailwindcss, vite, typescript, clsx/tailwind-merge; scripts `dev`, `build`, `preview` (preview/dev on :5173).
- `frontend/package-lock.json`: committed lockfile (required by CI `npm ci`).
- `frontend/index.html`
- `frontend/tsconfig.json`, `frontend/tsconfig.node.json`
- `frontend/vite.config.ts`: dev server + preview on port 5173.
- `frontend/tailwind.config.ts`: brand color tokens (teal/coral/bluegrey/taupe/bg-soft + hovers).
- `frontend/postcss.config.js`
- `frontend/Dockerfile`
- `frontend/.env.example`: `VITE_API_URL`.
- `frontend/src/main.tsx`: mounts router.
- `frontend/src/App.tsx`: route table (`/` → bootstrap, `/order/:id` → setup page).
- `frontend/src/index.css`: Tailwind directives.
- `frontend/src/config/constants.ts`: API base URL, i18n-ready strings.
- `frontend/src/lib/utils.ts`: `cn()` helper.
- `frontend/src/api/client.ts`: typed fetch wrapper + error mapping (network, 404, 422, 5xx, unexpected shapes).
- `frontend/src/api/orders.ts`: `createOrder`, `getOrder`, `addMenuItem`, `removeMenuItem`.
- `frontend/src/api/types.ts`: `OrderRead`, `MenuItem`, `MenuItemCreate`.
- `frontend/src/ui/button.tsx`, `input.tsx`, `label.tsx`, `card.tsx`, `badge.tsx`, `separator.tsx`.
- `frontend/src/icons/index.ts`: lucide re-exports.
- `frontend/src/components/TopBar.tsx`
- `frontend/src/components/MenuItemForm.tsx`
- `frontend/src/components/MenuItemList.tsx`
- `frontend/src/components/MenuItemRow.tsx`
- `frontend/src/components/EmptyState.tsx`
- `frontend/src/components/GenerateLinkSection.tsx`
- `frontend/src/pages/OrderBootstrap.tsx`
- `frontend/src/pages/OrderSetupPage.tsx`
- `frontend/src/hooks/useOrder.ts`

**E2E / UAT**
- `e2e/package.json`: `@playwright/test`.
- `e2e/package-lock.json`
- `e2e/playwright.config.ts`: baseURL from `BASE_URL`, `webServer` serving frontend on :5173, screenshot-on-failure.
- `e2e/tests/menu-setup.spec.ts`: STORY-1 E2E specs (one per AC + an edge case).
- `e2e/uat/STORY-1.feature`: Gherkin scenarios (UAT OPTIONAL).
- `e2e/uat/STORY-1-manual-uat.md`: manual UAT script.

**Root**
- `docker-compose.yml`: frontend + backend + postgres:16.
- `.env.example`: `DATABASE_URL`, `RESTAURANT_NAME`, `BACKEND_PORT`, `FRONTEND_PORT`, `VITE_API_URL`, `CORS_ORIGINS`.

### Modified files
- None. (Greenfield scaffold feature; `.github/workflows/ci.yml` is **not** modified — the scaffold conforms to it. `CLAUDE.md`, `.mcp.json`, `docs/prototype/` are left untouched.)

## Testing Strategy

- **Unit tests:** Service-layer business logic and Pydantic schema validation — `MenuItemService.add_item` (happy path; optional/empty price allowed; non-positive price rejected; blank name rejected; missing order → NotFound), `MenuItemService.remove_item` (success; missing item → NotFound), `OrderService.create_order`/`get_order` (success; missing → NotFound), and `MenuItemCreate` schema (valid with price, valid without price, blank name, negative/non-numeric price, >2 decimals). DB mocked/stubbed at this tier.
  - Directory: `backend/tests/unit/`
  - Naming: `test_{method_or_action}_{scenario}_{expected_outcome}` (testing_standards §3).
- **Integration tests:** Router + repository against a real Postgres (per conftest fixtures). `POST /api/orders` → 201; `GET /api/orders/{id}` → 200 with items, 404 when missing; `POST .../menu-items` → 201 with price, 201 without price (null persisted), 422 on blank name, 422 on bad price, 404 on missing order; `DELETE .../menu-items/{item_id}` → 204, 404 when missing. Round-trip persistence (add then read shows the item; price stored as NUMERIC and round-trips as null when omitted).
  - Directory: `backend/tests/integration/` (Integration Tests ENABLED per CLAUDE.md).
- **E2E tests:** Browser flow through the UI on `/order/:id`. Each AC has at least one spec, plus an edge case.
  - Directory: `e2e/tests/`
  - File: `e2e/tests/menu-setup.spec.ts` (E2E ENABLED per CLAUDE.md).
- **UAT scenarios:** Gherkin + manual script, one scenario per AC plus one edge case. UAT is OPTIONAL per CLAUDE.md — generated as artifacts, not wired to a BDD runner (executable browser coverage lives in the E2E specs).
  - Directory: `e2e/uat/`

## Acceptance Test Outline

| # | Acceptance Criterion | E2E Strategy | UAT Scenario Sketch |
|---|---|---|---|
| 1 | App load with no active order shows hardcoded restaurant name + empty form | Visit `/`; assert redirect to `/order/:id`; assert `data-testid="topbar-restaurant-name"` shows the configured name and is not an editable input; assert `data-testid="menu-list-empty"` empty state is shown | Given I open the app with no active order, When the page loads, Then I see the restaurant name displayed (not editable) and an empty menu-entry form |
| 2 | Add item with name (req), optional price, optional category | Fill `menuitemform-name`, `menuitemform-price`, `menuitemform-category`, click `menuitemform-add`; also add a second item leaving price blank; assert both appear | Given I am on the menu setup, When I enter a name (and optionally a price and category) and click Add, Then the item is added to the list |
| 3 | Empty name blocks + inline error; empty price allowed; bad price blocks + inline error | Click Add with blank name → assert `menuitemform-name-error` visible and list count unchanged; enter name + non-numeric/negative price → assert `menuitemform-price-error` and no add; enter name + blank price → asserts item added | Given a blank name, When I click Add, Then I see a name error and nothing is added; And a blank price is accepted; And a negative price shows a price error |
| 4 | Added item appears immediately showing name, price-if-present, category-if-present | After adding, assert row `menuitem-row-{id}` shows name; price element present only when a price was entered; category Badge present only when category entered | Given I added an item, Then it appears in the list below the form with its name, its price if provided, and its category if provided |
| 5 | Remove any item before sharing; list updates immediately | Click `menuitem-remove-{id}`; assert the row is gone and list count decremented immediately | Given items in the list, When I remove one, Then it disappears from the list immediately |
| 6 | Generate-link disabled until ≥1 valid item | With empty list assert `generatelink-button` is disabled and helper text "Add at least one menu item first." shown; after adding one item assert the button becomes enabled (edge case: remove the last item → button disabled again) | Given no menu items, Then the generate-link action is disabled; When I add at least one item, Then it becomes enabled |
