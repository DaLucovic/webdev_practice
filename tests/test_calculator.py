"""Unit tests for the calculator service (evaluate function)."""

import pytest

from app.services.calculator import ExpressionError, evaluate


class TestValidExpressions:
    """evaluate() returns the correct float for well-formed expressions."""

    def test_addition(self) -> None:
        assert evaluate("2 + 3") == 5.0

    def test_subtraction(self) -> None:
        assert evaluate("10 - 4") == 6.0

    def test_multiplication(self) -> None:
        assert evaluate("3 * 4") == 12.0

    def test_division(self) -> None:
        assert evaluate("10 / 4") == 2.5

    def test_floor_division(self) -> None:
        assert evaluate("7 // 2") == 3.0

    def test_modulo(self) -> None:
        assert evaluate("10 % 3") == 1.0

    def test_exponentiation(self) -> None:
        assert evaluate("2 ** 8") == 256.0

    def test_operator_precedence(self) -> None:
        assert evaluate("2 + 3 * 4") == 14.0

    def test_parentheses_override_precedence(self) -> None:
        assert evaluate("(2 + 3) * 4") == 20.0

    def test_nested_parentheses(self) -> None:
        assert evaluate("((2 + 3) * (4 - 1))") == 15.0

    def test_unary_minus(self) -> None:
        assert evaluate("-5") == -5.0

    def test_unary_plus(self) -> None:
        assert evaluate("+5") == 5.0

    def test_float_literals(self) -> None:
        assert evaluate("2.5 * 2") == 5.0

    def test_negative_result(self) -> None:
        assert evaluate("3 - 10") == -7.0

    def test_integer_division_produces_float(self) -> None:
        assert evaluate("6 / 2") == 3.0


class TestInvalidExpressions:
    """evaluate() raises ExpressionError for expressions it cannot handle."""

    def test_division_by_zero(self) -> None:
        with pytest.raises(ExpressionError, match="Division by zero"):
            evaluate("1 / 0")

    def test_floor_division_by_zero(self) -> None:
        with pytest.raises(ExpressionError, match="Division by zero"):
            evaluate("5 // 0")

    def test_modulo_by_zero(self) -> None:
        with pytest.raises(ExpressionError, match="Division by zero"):
            evaluate("5 % 0")

    def test_syntax_error_incomplete_expression(self) -> None:
        with pytest.raises(ExpressionError, match="Syntax error"):
            evaluate("2 +")

    def test_syntax_error_mismatched_parens(self) -> None:
        with pytest.raises(ExpressionError, match="Syntax error"):
            evaluate("(2 + 3")

    def test_variable_name_rejected(self) -> None:
        with pytest.raises(ExpressionError):
            evaluate("x + 1")

    def test_function_call_rejected(self) -> None:
        with pytest.raises(ExpressionError):
            evaluate("sqrt(4)")

    def test_string_literal_rejected(self) -> None:
        with pytest.raises(ExpressionError):
            evaluate('"hello"')

    def test_exponent_above_limit(self) -> None:
        with pytest.raises(ExpressionError, match="Exponent"):
            evaluate("2 ** 9999")

    def test_exponent_negative_above_limit(self) -> None:
        with pytest.raises(ExpressionError, match="Exponent"):
            evaluate("2 ** -9999")

    def test_bitwise_operator_rejected(self) -> None:
        with pytest.raises(ExpressionError):
            evaluate("4 & 2")
