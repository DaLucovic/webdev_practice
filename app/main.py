"""Entry point for the Expression Calculator API.

Start the server with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app.routes.calculator import router as calculator_router
from app.routes.history import router as history_router

app = FastAPI(
    title="Expression Calculator API",
    description="Safely evaluates mathematical expressions via a REST endpoint.",
    version="1.0.0",
)

app.include_router(calculator_router)
app.include_router(history_router)


@app.get("/health", tags=["health"], status_code=200)
def health() -> dict[str, str]:
    """Liveness probe — returns 200 when the server is running."""
    return {"status": "ok"}

if __name__ == "__main__":
  import uvicorn
  uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

