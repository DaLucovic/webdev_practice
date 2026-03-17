# Project Review — Expression Calculator

> Reviewed against production standards. Written to be critical and specific,
> not encouraging. The goal is to identify exactly what would need to change
> before this ran in a real environment.
>
> For explanations of how the project is structured, see **GUIDE.md**.

---

## 1. Architectural Decisions

### What was done right

**Service layer separation is genuine, not cosmetic.**
`evaluate()` takes a plain `str` and returns a plain `float`. It knows nothing
about HTTP, FastAPI, or Pydantic. The route constructs the response model
itself. This means the evaluator could be used in a CLI, a background worker,
or a different web framework without modification. Many projects claim this
separation but then have services that import `Request` objects — this one
doesn't.

**The AST evaluator is the correct approach.**
Using `eval()` for a calculator API is a serious security vulnerability — any
user can execute arbitrary Python. The whitelist-based AST walker allows only
the exact node types needed. The exponent guard (`_MAX_EXPONENT = 1000`) is a
concrete safety measure against `2 ** 9999999` hanging the process.
`math.isnan()` and `math.isinf()` checks prevent silent bad results from
floating out.

**The history service is structured for replacement.**
The module-level `_store` list is explicitly called out as a singleton. The
public interface — `record()`, `get_all()`, `clear()` — maps directly to what
a database layer would expose. Swapping it requires changing one file, not
hunting through routes and models.

**Vite proxy and nginx proxy are consistent.**
Both strip `/api/` and forward to the backend on port 8000. The developer
experience in `npm run dev` is functionally identical to the Docker production
setup. This is the right way to handle CORS in a frontend+backend project —
avoid CORS headers entirely by having the same origin serve everything.

**Test structure is layered correctly.**
Unit tests hit the service functions directly. Integration tests use
`TestClient` and go through the full HTTP stack. The `autouse` history fixture
means no test can leak state into the next. The `conftest.py` keeps fixtures
in one place.

---

## 2. Real Problems — What Would Fail in Production

### 2.1 The in-memory store is not a store, it is a variable

`_store: list[HistoryEntry] = []` lives in the Python process. Every time the
container restarts, history is gone. With multiple uvicorn workers
(`--workers 4`), each worker has its own `_store` — requests round-robin across
workers and history appears to randomly lose entries. This is the single largest
architectural gap. It's not a scalability issue, it is a correctness issue under
any multi-worker setup.

### 2.2 No rate limiting

`POST /calculate` is CPU-bound (AST parsing and evaluation). There is nothing
preventing a client from sending 10,000 requests per second. The
`_MAX_EXPONENT` guard protects against one class of abuse, but not volume. A
single malicious or buggy client could saturate the container. In production
this would need a rate limiter at the nginx level (`limit_req_zone`) or a
FastAPI middleware (`slowapi` is the common choice).

### 2.3 DELETE /history has no access control

Any client that can reach the API can wipe all history for all users. There is
no authentication, no concept of user ownership, no confirmation. On a
public-facing deployment this is a one-request denial of service on the history
feature.

### 2.4 GET /history has no pagination

`get_all()` returns every entry as a list. At 1,000 entries this is fine. At
100,000 entries this serialises the entire table into a single JSON response on
every request. The endpoint needs `limit` and `offset` query parameters (or
cursor-based pagination) before it can be called production-ready.

### 2.5 Two different error shapes from the same status code

When Pydantic rejects an empty expression, the response is:
```json
{"detail": [{"loc": ["body", "expression"], "msg": "...", "type": "..."}]}
```

When the service rejects `1/0`, the response is:
```json
{"detail": "Division by zero is undefined."}
```

Both are 422. The frontend's `extractErrorMessage()` handles this with a type
check, but any other client has to special-case it too. A production API should
return a consistent error envelope. FastAPI's `exception_handler` can intercept
`RequestValidationError` and reformat it to match the `HTTPException` shape.

### 2.6 `--reload` is in the production entry point

`app/main.py` line 28:
```python
uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

`reload=True` starts a file watcher that polls the filesystem every second.
This is a development convenience that increases CPU usage and risks restarting
mid-request in production. The `if __name__ == "__main__"` block is only used
locally (the Dockerfile uses the `CMD` form), so this won't kill the container
— but someone running `python -m app.main` in production would get a
hot-reloading server without realising it.

### 2.7 docker-compose has no health checks or restart policy

```yaml
depends_on:
  - backend
```

This waits for the `backend` container to *start*, not for FastAPI to be
*ready*. If uvicorn takes 2 seconds to start, nginx may begin proxying before
FastAPI is accepting connections, causing the first few requests to fail.
The fix:

```yaml
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 5s
    retries: 3

frontend:
  depends_on:
    backend:
      condition: service_healthy
```

There is also no `restart: unless-stopped`. A crashed container stays down
until someone manually intervenes.

### 2.8 Double HTTP request after every calculation

In `App.tsx`, after a successful calculation:
```typescript
const response = await calculate(expression);   // POST /calculate
const updated = await getHistory();             // GET /history
```

Two sequential HTTP requests for what is conceptually one user action. The
backend already returns the full result in the `POST /calculate` response —
the new history entry could be prepended to the local state optimistically
instead of re-fetching. This also means any calculation under poor network
conditions has double the latency before the UI updates.

### 2.9 No frontend tests

The backend has 57 test cases across three files. The frontend has zero. The
`api/` module (`calculate`, `getHistory`, `clearHistory`) has non-trivial
branching logic in `extractErrorMessage`. Components have conditional rendering
paths. None of this is verified. Vitest and React Testing Library are the
standard tools for this stack.

### 2.10 TypeScript interfaces are manually synced with Pydantic models

`frontend/src/types/calculator.ts` is a hand-written copy of
`app/models/calculator.py`. When the backend model changes, the frontend type
must be updated manually. There is no mechanism to detect the mismatch. Tools
like `openapi-typescript` can generate TypeScript types automatically from
FastAPI's OpenAPI schema — this eliminates the entire class of
"backend changed, frontend didn't" bugs.

### 2.11 CORS is not configured on the backend

The current setup works because nginx proxies everything from the same origin.
But if someone calls the backend API directly (e.g. `http://localhost:8000`
from a browser during development without the Vite proxy, or from a different
domain), CORS will block it. The backend has no `CORSMiddleware`. This is
latent and will surface the moment the deployment topology changes.

---

## 3. Scalability Assessment

| Concern | Current state | Would break at |
|---|---|---|
| Request throughput | Single uvicorn worker | ~500 concurrent users |
| History storage | In-memory list | Any restart / multiple workers |
| History retrieval | Full list serialised per request | ~10,000 entries |
| Expression evaluation | Synchronous, CPU-bound | Sustained high concurrency |
| Container restarts | No restart policy | First crash |

The evaluator itself scales well — it is pure computation with no I/O and no
shared state. The bottleneck is the history store, which is fundamentally
incompatible with horizontal scaling. Everything else is addressable with
configuration.

---

## 4. What Changes With a Database

### The minimal path: SQLite → PostgreSQL

The history service (`app/services/history.py`) is the only file that touches
storage. Its public interface stays identical. Internally:

```
Before                          After
──────────────────────          ──────────────────────────────────────
_store: list[HistoryEntry]      SQLAlchemy session
record() → append to list       INSERT INTO calculations ...
get_all() → list(_store)        SELECT * FROM calculations ORDER BY ...
clear() → _store.clear()        DELETE FROM calculations
```

**New files needed:**
- `app/db/session.py` — database engine and session factory
- `app/db/models.py` — SQLAlchemy ORM models (separate from Pydantic models)
- `alembic/` — migration directory (`alembic init`, then one migration per schema change)

**Files that change:**
- `app/services/history.py` — replace list operations with ORM queries
- `requirements.txt` — add `sqlalchemy`, `alembic`, and a driver (`psycopg2-binary` or `asyncpg`)
- `docker-compose.yml` — add a `db` service (`postgres:16-alpine`)

**What does NOT change:**
- `app/routes/history.py` — zero changes, it calls the same service interface
- `app/models/calculator.py` — Pydantic schemas are independent of the ORM
- All frontend files — the API contract is unchanged
- All existing tests — service tests would be replaced, route tests stay identical

**New problems a database introduces:**
- Pagination becomes mandatory (you now have persistent storage that grows forever)
- Migrations must be run before the app starts (init container or startup check)
- Connection pooling needs configuration under load
- The `db` container needs a volume, or data is lost on restart anyway:
  ```yaml
  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
  volumes:
    postgres_data:
  ```
- Tests need a separate test database or transaction rollback between tests

---

## 5. Prioritised Improvements

Ordered by impact, not effort.

**Do before any real users:**
1. Add `restart: unless-stopped` and health checks to `docker-compose.yml`
2. Fix the error response shape inconsistency with a custom exception handler
3. Add pagination to `GET /history` (`?limit=50&offset=0`)
4. Add `CORSMiddleware` to `app/main.py` with explicit origin allowlist

**Do before any scale:**
5. Replace in-memory store with SQLite (easy) or PostgreSQL (production)
6. Add rate limiting — `slowapi` for FastAPI, `limit_req_zone` for nginx
7. Add uvicorn `--workers` flag (at least match CPU count)
8. Optimistic history update in `App.tsx` (eliminate the second fetch)

**Do for maintainability:**
9. Generate TypeScript types from OpenAPI schema (`openapi-typescript`)
10. Add frontend tests with Vitest and React Testing Library
11. Remove `reload=True` from `__main__` block
12. Add structured logging (replace default uvicorn logs with `structlog`)
