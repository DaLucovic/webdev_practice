"""Unit tests for the history service."""

from datetime import timezone

from app.services import history as history_service


class TestRecord:
    """history_service.record() stores entries correctly."""

    def test_record_returns_entry(self) -> None:
        entry = history_service.record("1 + 1", 2.0)
        assert entry.expression == "1 + 1"
        assert entry.result == 2.0

    def test_record_timestamp_is_utc(self) -> None:
        entry = history_service.record("1 + 1", 2.0)
        assert entry.timestamp.tzinfo == timezone.utc

    def test_record_adds_to_store(self) -> None:
        history_service.record("1 + 1", 2.0)
        assert len(history_service.get_all()) == 1

    def test_multiple_records_stored_in_order(self) -> None:
        history_service.record("1 + 1", 2.0)
        history_service.record("2 * 3", 6.0)
        entries = history_service.get_all()
        assert entries[0].expression == "1 + 1"
        assert entries[1].expression == "2 * 3"


class TestGetAll:
    """history_service.get_all() returns a safe snapshot."""

    def test_empty_store_returns_empty_list(self) -> None:
        assert history_service.get_all() == []

    def test_returns_all_entries(self) -> None:
        history_service.record("1 + 1", 2.0)
        history_service.record("3 * 3", 9.0)
        assert len(history_service.get_all()) == 2

    def test_returns_copy_not_reference(self) -> None:
        """Mutating the returned list must not affect the internal store."""
        history_service.record("1 + 1", 2.0)
        snapshot = history_service.get_all()
        snapshot.clear()
        assert len(history_service.get_all()) == 1


class TestClear:
    """history_service.clear() empties the store and reports the count."""

    def test_clear_returns_deleted_count(self) -> None:
        history_service.record("1 + 1", 2.0)
        history_service.record("2 + 2", 4.0)
        assert history_service.clear() == 2

    def test_clear_empties_store(self) -> None:
        history_service.record("1 + 1", 2.0)
        history_service.clear()
        assert history_service.get_all() == []

    def test_clear_on_empty_store_returns_zero(self) -> None:
        assert history_service.clear() == 0

    def test_clear_then_record_works(self) -> None:
        history_service.record("1 + 1", 2.0)
        history_service.clear()
        history_service.record("9 * 9", 81.0)
        entries = history_service.get_all()
        assert len(entries) == 1
        assert entries[0].expression == "9 * 9"
