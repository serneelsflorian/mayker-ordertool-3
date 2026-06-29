# Refactor Gate Report — STORY-1

**Feature:** Admin starts a group order and enters the menu  
**Date:** 2026-06-29  
**Scope:** New files added in `feature/STORY-1-admin-starts-group-order`

## Findings

| # | File | Finding | Category | Severity | Resolution |
|---|------|---------|----------|----------|------------|
| 1 | `backend/app/core/exception_handlers.py` | `_error_response` and `_status_from_code` were defined but never called — both public handlers constructed their `JSONResponse` inline, making the helpers dead code. | Dead code | RECOMMENDED | Applied — removed both functions and the unused `from typing import Any` import. |
| 2 | `backend/app/services/order_service.py`, `menu_item_service.py` | Module-level singleton repositories (`_order_repository`, `_menu_item_repository`) were instantiated at import time and then used only as constructor defaults, adding unnecessary module-scope state. | DRY / Architecture | RECOMMENDED | Applied — removed module-level singletons; services now instantiate their default repo inside `__init__` using `if arg is not None else RepoClass()`. |
| 3 | `backend/app/routers/orders.py` | `get_settings().RESTAURANT_NAME` was called twice (once per endpoint). Since `get_settings` is `@lru_cache` the cost is negligible, but the repetition is a minor DRY smell. | DRY | RECOMMENDED | Deferred — assigning `_settings = get_settings()` at module level re-introduces the `DATABASE_URL`-at-import-time problem that was fixed in the preceding commit (`fix(STORY-1): lazy-load settings in main.py`). The two `get_settings()` calls remain; the cache makes them effectively free. Documented here for follow-up in a future refactor pass. |
| 4 | `frontend/src/components/GenerateLinkSection.tsx` | Inline `// STORY-2 will implement the actual link generation` comment inside a production component. Story-tracking notes belong in the issue tracker, not in source code. | Dead code | RECOMMENDED | Applied — removed the comment; the empty `onClick` handler is self-evident as a placeholder. |
| 5 | `frontend/src/components/MenuItemForm.tsx` | `validatePrice` checked `value === undefined` for a parameter typed `string` — an unreachable branch. | Dead code | OPTIONAL | Not applied (OPTIONAL severity). Noted for awareness; the dead branch is harmless. |
| 6 | `backend/app/routers/orders.py`, `menu_items.py` | `session.commit()` was called in every router handler instead of in the service layer, violating the layered-architecture rule that transactional boundaries belong in services. | Layered-architecture drift | RECOMMENDED | Applied — moved `await session.commit()` into each service method (`OrderService.create_order`, `MenuItemService.add_item`, `MenuItemService.remove_item`); removed the redundant calls from both routers. All 19 unit tests pass after the change. |

## Test Results After Refactor

```
19 passed in 0.02s  (backend/tests/unit/)
TypeScript: 0 errors (frontend tsc --noEmit)
```

## Summary

5 of 5 RECOMMENDED findings were either applied or explicitly deferred with documented rationale. 1 OPTIONAL finding noted but not applied. No behaviour-preserving changes were skipped without explanation.
