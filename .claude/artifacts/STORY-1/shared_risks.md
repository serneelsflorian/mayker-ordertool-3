# Shared Risk Analysis, STORY-1

> STORY-1 is the **scaffold feature** and is alone in Wave 1. It has no in-wave peers to collide with, but it lays the **foundation** that every later story (STORY-2..7) builds on. The risk is not concurrent edits — it is that decisions made here ripple forward. The foundational surfaces are flagged explicitly below.

## Files this feature will create

**Backend (FastAPI / SQLAlchemy 2.x async / Pydantic v2 / Alembic)**
- `backend/requirements.txt`
- `backend/Dockerfile`, `backend/.env.example`
- `backend/alembic.ini`, `backend/alembic/env.py`, `backend/alembic/script.py.mako`, `backend/alembic/versions/0001_create_orders_and_menu_items.py`
- `backend/app/main.py`, `backend/app/__init__.py`
- `backend/app/core/{config,logging,exceptions,exception_handlers}.py`
- `backend/app/db/{base,session}.py`
- `backend/app/models/{order,menu_item}.py`
- `backend/app/schemas/{order,menu_item}.py`
- `backend/app/repositories/{order_repository,menu_item_repository}.py`
- `backend/app/services/{order_service,menu_item_service}.py`
- `backend/app/routers/{orders,menu_items}.py`
- `backend/tests/conftest.py`, `backend/tests/unit/*`, `backend/tests/integration/*`

**Frontend (Vite / React / TS / Tailwind / React Router)**
- `frontend/{package.json,package-lock.json,index.html,tsconfig.json,tsconfig.node.json,vite.config.ts,tailwind.config.ts,postcss.config.js,Dockerfile,.env.example}`
- `frontend/src/{main.tsx,App.tsx,index.css}`
- `frontend/src/config/constants.ts`, `frontend/src/lib/utils.ts`
- `frontend/src/api/{client,orders,types}.ts`
- `frontend/src/ui/{button,input,label,card,badge,separator}.tsx`
- `frontend/src/icons/index.ts`
- `frontend/src/components/{TopBar,MenuItemForm,MenuItemList,MenuItemRow,EmptyState,GenerateLinkSection}.tsx`
- `frontend/src/pages/{OrderBootstrap,OrderSetupPage}.tsx`
- `frontend/src/hooks/useOrder.ts`

**E2E / UAT**
- `e2e/{package.json,package-lock.json,playwright.config.ts}`
- `e2e/tests/menu-setup.spec.ts`
- `e2e/uat/{STORY-1.feature,STORY-1-manual-uat.md}`

**Root**
- `docker-compose.yml`
- `.env.example`

## Existing files this feature will modify
- **None.** Greenfield scaffold. `.github/workflows/ci.yml` is intentionally NOT modified (the scaffold conforms to it; see plan "CI Pipeline Configuration"). `CLAUDE.md`, `.mcp.json`, `.claude/project_state.json`, and `docs/prototype/` are left untouched.

## Potential conflicts with other features in the same wave
- **None in-wave.** STORY-1 is the sole Wave 1 feature.

## Foundational surfaces — changes here ripple to STORY-2..7

These are created by STORY-1 and consumed (not re-created) by later stories. Treat them as a stable contract; later stories should extend, not reshape, them. Reshaping any of these is a breaking change that ripples across multiple later stories:

1. **Project file layout** (`backend/app/{routers,services,repositories,schemas,models,core,db}`, `frontend/src/{api,ui,components,pages,hooks,icons}`, `e2e/`) — every later story adds files into these directories. Renaming or restructuring them later forces edits across STORY-2..7.
2. **`Order` and `MenuItem` ORM models + the DB schema/migration** (`orders`, `menu_items` with nullable `price NUMERIC(10,2)`, status `open/closed`, cascade FK). STORY-3..6 (guest selections, order overview, close order, export/email) all extend this schema (e.g. guests, guest selections, notes, quantities, closed-state enforcement). Adding to it is fine; altering STORY-1's columns/constraints later requires new migrations layered on `0001`.
3. **The REST API contract + global error shape** (`/api/orders`, `/api/orders/{id}`, `/api/orders/{id}/menu-items[...]`, and `{ "error": { code, message, details } }`). STORY-2 surfaces the order id as a share link; STORY-3..6 add guest/selection/close/export endpoints under the same order resource. The error envelope and resource shape established here are the contract those stories extend.
4. **The frontend api-client module** (`frontend/src/api/{client,orders,types}.ts`). All later frontend features call through this typed client; its error-mapping and base-URL conventions are reused. Changing its shape later touches every consumer.
5. **The `/order/:id` route + root bootstrap** (`frontend/src/App.tsx`, `OrderBootstrap`, `OrderSetupPage`). STORY-2's share link points at `/order/:id`; STORY-3's guest view and STORY-4/5's overview/close all live under this route. The routing contract is foundational.
6. **Tailwind brand config** (`frontend/tailwind.config.ts` — teal/coral/bluegrey/taupe/bg-soft tokens). Every later screen styles against these tokens. Renaming tokens later forces sweeping className changes.
7. **Shared test infrastructure** (`backend/tests/conftest.py` Postgres + httpx async client + migration runner + rollback isolation; `e2e/playwright.config.ts`). All later backend/E2E tests depend on these fixtures.

### Foundational decision: price is OPTIONAL (nullable)
STORY-1 establishes that **menu-item price is optional and stored nullable** (`price NUMERIC(10,2)` nullable; validated positive/≤2-decimals only when present). This **diverges from the design prototype**, which makes price required and positive — the builder must follow the acceptance criteria, not the prototype. Later stories read against this contract:
- **STORY-3/4 (guest selections, subtotals):** subtotal/total computation must treat a missing price as "no price" (e.g. excluded or treated as 0) rather than assuming every item has a price. Any later story computing totals MUST handle `price = null`.
- **STORY-6 (export/email):** consolidated export lines must render with or without a price. Per CLAUDE.md the export merge rule keys on item + note exactly; that is a STORY-6 concern, but it must coexist with nullable prices established here.

### Foundational decision: server-persisted state (no localStorage)
STORY-1 persists the order and its menu items in Postgres via the backend and keys state by the order id in `/order/:id` (CLAUDE.md fixed decision #1). **No localStorage/sessionStorage** is used for order state. Every later story inherits this: guest selections, overview, close, and export must all read/write through the backend so state is shared across browsers/sessions and survives refresh. A later story reintroducing client-only state would violate the fixed architecture.
