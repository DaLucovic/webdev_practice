# Project Guide — Expression Calculator

> Plain-language explanations of how this project is structured and how its
> pieces fit together. No assumed prior knowledge.

---

## 1. Project Map — Goal of Every File and Folder

```
webdev/
│
├── app/                          # FastAPI application (Python package)
│   ├── main.py                   # App factory: creates FastAPI instance, registers routers
│   ├── models/
│   │   └── calculator.py         # Pydantic schemas — the contract between HTTP and Python
│   ├── routes/
│   │   ├── calculator.py         # HTTP handler for POST /calculate — thin, no logic
│   │   └── history.py            # HTTP handlers for GET/DELETE /history — thin, no logic
│   └── services/
│       ├── calculator.py         # Core domain logic: AST-based expression evaluator
│       └── history.py            # In-memory store: record(), get_all(), clear()
│
├── tests/
│   ├── conftest.py               # Shared fixtures: TestClient, autouse history reset
│   ├── test_calculator.py        # Unit tests for evaluate() in isolation
│   ├── test_history.py           # Unit tests for the history store in isolation
│   └── test_routes.py            # Integration tests: full HTTP request → response
│
├── frontend/
│   ├── Dockerfile                # Multi-stage build: Node (build) → nginx (serve)
│   ├── nginx.conf                # Static file serving + /api/ proxy to backend container
│   ├── vite.config.ts            # Dev server config: /api/ proxy to localhost:8000
│   ├── .env                      # VITE_API_BASE_URL — baked in at build time
│   └── src/
│       ├── main.tsx              # DOM entry point: mounts <App /> into #root
│       ├── App.tsx               # Root component: owns all state, wires children
│       ├── App.css               # Global styles — all CSS lives here (one file)
│       ├── api/
│       │   └── calculator.ts     # All fetch() calls — the frontend's service layer
│       ├── types/
│       │   └── calculator.ts     # TypeScript interfaces mirroring Pydantic models
│       └── components/
│           ├── ExpressionInput.tsx   # Controlled input + submit button with spinner
│           ├── ResultDisplay.tsx     # Shows last successful result, null = renders nothing
│           ├── ErrorMessage.tsx      # Shows last error, null = renders nothing
│           └── HistoryList.tsx       # History section with clear button
│
├── Dockerfile                    # Backend image: python:3.12-slim + app code
├── docker-compose.yml            # Orchestrates backend + frontend containers
├── requirements.txt              # Runtime deps: fastapi, uvicorn, pydantic
├── requirements-dev.txt          # Dev/test deps: adds pytest, httpx
└── pytest.ini                    # Tells pytest where to find tests
```

---

## 2. Models, Routes, and Services — How They Relate

The backend is split into three layers. Each layer has one job and does not do
the other layers' jobs. Here is what each one is responsible for:

| Layer | Folder | Job |
|---|---|---|
| Models | `app/models/` | Describe the *shape* of data going in and out |
| Routes | `app/routes/` | Receive HTTP requests, call services, return responses |
| Services | `app/services/` | Do the actual work — math, storage, business logic |

The rule is: **data flows down, results flow up.**
Routes call services. Services never call routes. Models are used by both.

---

### Tracing a real request: `POST /calculate {"expression": "2 + 3"}`

**1. The request arrives at the route** (`app/routes/calculator.py`)

FastAPI matches the URL and method to this function:

```python
def calculate(request: CalculateRequest) -> CalculateResponse:
```

**2. The model validates the input** (`app/models/calculator.py`)

Before your code even runs, FastAPI feeds the JSON body through `CalculateRequest`:

```python
class CalculateRequest(BaseModel):
    expression: str = Field(..., min_length=1, max_length=256)
```

If `expression` is missing, empty, or not a string, Pydantic rejects it and
returns a 422 error automatically. Your route function never runs.
If it passes, `request.expression` is guaranteed to be a clean, non-empty string.

**3. The route calls the service** (`app/services/calculator.py`)

```python
result: float = evaluate(request.expression)
```

`evaluate()` knows nothing about HTTP, FastAPI, or Pydantic. It takes a plain
string, does the math, and returns a plain float. If the expression is invalid
it raises `ExpressionError` — a plain Python exception, not an HTTP concept.

The route catches it and translates it into HTTP language:

```python
except ExpressionError as exc:
    raise HTTPException(status_code=422, detail=str(exc))
```

This translation — from domain error to HTTP error — is the route's job, not
the service's.

**4. The route calls a second service** (`app/services/history.py`)

```python
history_service.record(request.expression, result)
```

The history service stores the entry. It also knows nothing about HTTP.

**5. The route returns a response model**

```python
return CalculateResponse(expression=request.expression, result=result)
```

FastAPI serialises `CalculateResponse` to JSON automatically:

```json
{"expression": "2 + 3", "result": 5.0}
```

---

### Why split it this way?

**Services can be tested without a web server.**
`evaluate("2 + 3")` is a plain function call. No HTTP client needed, no server
to start. That's why `test_calculator.py` just calls `evaluate()` directly.

**Services can be reused.**
`evaluate()` could be called from a CLI tool, a background job, or a different
web framework without changing a single line. The route is the only thing that
knows this is a web app.

**Routes stay readable.**
The route for `POST /calculate` is 7 lines of actual logic. You can read it
in 30 seconds and understand exactly what the endpoint does — because all the
complexity lives in the service.

**Models are the contract.**
`CalculateRequest` and `CalculateResponse` are the agreed shape of the API.
The frontend's TypeScript interfaces (`frontend/src/types/calculator.ts`) mirror
them. When you change a model, you know exactly what else needs updating.

---

### The same pattern in `GET /history` and `DELETE /history`

```python
# GET /history — app/routes/history.py
def get_history() -> list[HistoryEntry]:
    return history_service.get_all()          # one line, calls service, done

# DELETE /history
def clear_history() -> ClearHistoryResponse:
    deleted: int = history_service.clear()    # one line, calls service
    return ClearHistoryResponse(deleted=deleted)
```

Routes are intentionally boring. All the decisions live in the service.

---

## 3. How `docker compose up` Works

When you run `docker compose up`, Docker reads `docker-compose.yml` and
processes both services (`backend` and `frontend`). Here is what happens:

**Step 1 — Build each image.**
Docker follows each `Dockerfile` line by line. The numbered steps in the output
(`#1`, `#2`, `#21`...) correspond to those instructions. For the backend this
means installing Python packages; for the frontend it means installing Node
packages and running `npm run build` to compile the React app into static files.
Each step is **cached** — if nothing changed since the last build, Docker skips
it (`CACHED`). That's why rebuilds are faster the second time.

**Step 2 — Create containers from the built images.**
An *image* is a frozen snapshot (the blueprint). A *container* is a running
instance of that image — the same relationship as a program file vs a running
process.

**Step 3 — Start both containers.**
- The `backend` container boots uvicorn and FastAPI, listening on port 8000.
- The `frontend` container starts nginx, which serves the compiled React files
  and proxies any `/api/` request forward to the backend container.

**Step 4 — Stream live logs.**
Everything both containers print to stdout appears in your terminal, prefixed
by service name (`frontend-1 |`, `backend-1 |`).

**Port mapping in plain terms:**

| URL you visit | What handles it |
|---|---|
| `localhost:3000` | nginx → serves the compiled React app |
| `localhost:8000` | FastAPI directly |
| React calls `/api/...` | nginx proxies it → FastAPI on port 8000 |

The key thing to understand: `depends_on: backend` in `docker-compose.yml`
tells Docker to *start* the backend container before the frontend, but it does
not wait for FastAPI to be *ready and accepting connections*. See the production
review for why this matters.
