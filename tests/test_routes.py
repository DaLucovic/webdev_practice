"""Integration tests for all API routes via FastAPI TestClient."""

from fastapi.testclient import TestClient


class TestCalculateRoute:
    """POST /calculate — happy path and error cases."""

    def test_valid_expression_returns_200(self, client: TestClient) -> None:
        response = client.post("/calculate", json={"expression": "2 + 3"})
        assert response.status_code == 200

    def test_result_is_correct(self, client: TestClient) -> None:
        response = client.post("/calculate", json={"expression": "2 + 3 * 4"})
        assert response.json()["result"] == 14.0

    def test_response_echoes_expression(self, client: TestClient) -> None:
        response = client.post("/calculate", json={"expression": "10 / 2"})
        assert response.json()["expression"] == "10 / 2"

    def test_parentheses_respected(self, client: TestClient) -> None:
        response = client.post("/calculate", json={"expression": "(2 + 3) * 4"})
        assert response.json()["result"] == 20.0

    def test_float_result(self, client: TestClient) -> None:
        response = client.post("/calculate", json={"expression": "7 / 2"})
        assert response.json()["result"] == 3.5

    def test_negative_result(self, client: TestClient) -> None:
        response = client.post("/calculate", json={"expression": "3 - 10"})
        assert response.json()["result"] == -7.0

    def test_division_by_zero_returns_422(self, client: TestClient) -> None:
        response = client.post("/calculate", json={"expression": "1 / 0"})
        assert response.status_code == 422

    def test_division_by_zero_has_detail(self, client: TestClient) -> None:
        response = client.post("/calculate", json={"expression": "1 / 0"})
        assert "detail" in response.json()

    def test_invalid_syntax_returns_422(self, client: TestClient) -> None:
        response = client.post("/calculate", json={"expression": "2 +"})
        assert response.status_code == 422

    def test_empty_expression_returns_422(self, client: TestClient) -> None:
        response = client.post("/calculate", json={"expression": ""})
        assert response.status_code == 422

    def test_whitespace_only_returns_422(self, client: TestClient) -> None:
        response = client.post("/calculate", json={"expression": "   "})
        assert response.status_code == 422

    def test_expression_too_long_returns_422(self, client: TestClient) -> None:
        response = client.post("/calculate", json={"expression": "1+" * 200})
        assert response.status_code == 422

    def test_variable_name_returns_422(self, client: TestClient) -> None:
        response = client.post("/calculate", json={"expression": "x + 1"})
        assert response.status_code == 422

    def test_function_call_returns_422(self, client: TestClient) -> None:
        response = client.post("/calculate", json={"expression": "sqrt(4)"})
        assert response.status_code == 422

    def test_missing_body_returns_422(self, client: TestClient) -> None:
        response = client.post("/calculate")
        assert response.status_code == 422

    def test_successful_calculation_recorded_in_history(
        self, client: TestClient
    ) -> None:
        client.post("/calculate", json={"expression": "2 + 2"})
        history = client.get("/history").json()
        assert any(e["expression"] == "2 + 2" for e in history)

    def test_failed_calculation_not_recorded_in_history(
        self, client: TestClient
    ) -> None:
        client.post("/calculate", json={"expression": "1 / 0"})
        assert client.get("/history").json() == []


class TestHistoryRoute:
    """GET /history and DELETE /history."""

    def test_empty_history_returns_200(self, client: TestClient) -> None:
        response = client.get("/history")
        assert response.status_code == 200

    def test_empty_history_returns_empty_list(self, client: TestClient) -> None:
        assert client.get("/history").json() == []

    def test_history_contains_entry_after_calculation(
        self, client: TestClient
    ) -> None:
        client.post("/calculate", json={"expression": "5 * 5"})
        entries = client.get("/history").json()
        assert len(entries) == 1
        assert entries[0]["expression"] == "5 * 5"
        assert entries[0]["result"] == 25.0

    def test_history_preserves_insertion_order(self, client: TestClient) -> None:
        client.post("/calculate", json={"expression": "1 + 1"})
        client.post("/calculate", json={"expression": "2 * 3"})
        entries = client.get("/history").json()
        assert entries[0]["expression"] == "1 + 1"
        assert entries[1]["expression"] == "2 * 3"

    def test_history_entry_has_timestamp(self, client: TestClient) -> None:
        client.post("/calculate", json={"expression": "1 + 1"})
        entry = client.get("/history").json()[0]
        assert "timestamp" in entry
        assert entry["timestamp"] is not None

    def test_delete_returns_200(self, client: TestClient) -> None:
        response = client.delete("/history")
        assert response.status_code == 200

    def test_delete_returns_deleted_count(self, client: TestClient) -> None:
        client.post("/calculate", json={"expression": "1 + 1"})
        client.post("/calculate", json={"expression": "2 + 2"})
        response = client.delete("/history")
        assert response.json()["deleted"] == 2

    def test_delete_empties_history(self, client: TestClient) -> None:
        client.post("/calculate", json={"expression": "1 + 1"})
        client.delete("/history")
        assert client.get("/history").json() == []

    def test_delete_on_empty_history_returns_zero(self, client: TestClient) -> None:
        response = client.delete("/history")
        assert response.json()["deleted"] == 0


class TestHealthRoute:
    """GET /health — liveness probe."""

    def test_health_returns_200(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_ok_status(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.json() == {"status": "ok"}
