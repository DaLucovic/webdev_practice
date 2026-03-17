"""In-memory store for completed calculations.

The module-level ``_store`` list acts as a process-scoped singleton.
To swap this for a database later, replace only this module's implementation
while keeping the public interface (``record``, ``get_all``, ``clear``) intact.
"""

from datetime import datetime, timezone

from app.models.calculator import HistoryEntry

_store: list[HistoryEntry] = []


def record(expression: str, result: float) -> HistoryEntry:
    """Append a completed calculation to the in-memory store.

    Args:
        expression: The expression string that was evaluated.
        result: The numeric result of the evaluation.

    Returns:
        The newly created ``HistoryEntry``.
    """
    entry = HistoryEntry(
        expression=expression,
        result=result,
        timestamp=datetime.now(timezone.utc),
    )
    _store.append(entry)
    return entry


def get_all() -> list[HistoryEntry]:
    """Return a snapshot of all history entries in insertion order (oldest first).

    Returns:
        A shallow copy of the internal store so callers cannot mutate it.
    """
    return list(_store)


def clear() -> int:
    """Remove all history entries.

    Returns:
        The number of entries that were deleted.
    """
    count = len(_store)
    _store.clear()
    return count
