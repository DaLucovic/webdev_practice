"""History routes: GET /history, DELETE /history."""

from fastapi import APIRouter

from app.models.calculator import ClearHistoryResponse, HistoryEntry
from app.services import history as history_service

router = APIRouter(prefix="/history", tags=["history"])


@router.get(
    "",
    response_model=list[HistoryEntry],
    status_code=200,
    summary="Retrieve calculation history",
    response_description="All past calculations in insertion order (oldest first).",
)
def get_history() -> list[HistoryEntry]:
    """Return every calculation recorded since the server started.

    Entries are ordered oldest-first.  An empty list is returned when no
    calculations have been performed yet.
    """
    return history_service.get_all()


@router.delete(
    "",
    response_model=ClearHistoryResponse,
    status_code=200,
    summary="Clear calculation history",
    response_description="Number of entries that were deleted.",
)
def clear_history() -> ClearHistoryResponse:
    """Delete all stored calculation history entries.

    Returns the count of deleted entries so callers can confirm the operation.
    """
    deleted: int = history_service.clear()
    return ClearHistoryResponse(deleted=deleted)
