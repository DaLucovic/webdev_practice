"""Safe arithmetic expression evaluator using Python's AST module.

Expressions are parsed into an abstract syntax tree and walked node-by-node
against an explicit whitelist.  No use of eval() or exec().
"""

import ast
import math
import operator
from collections.abc import Callable

# Cap on exponent magnitude to prevent operations like 2**9999999 hanging the process.
_MAX_EXPONENT: int = 1_000

# Type aliases for the operator lookup tables.
_BinaryOp = Callable[[float, float], float]
_UnaryOp = Callable[[float], float]

_BINARY_OPS: dict[type, _BinaryOp] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.FloorDiv: operator.floordiv,
}

_UNARY_OPS: dict[type, _UnaryOp] = {
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


class ExpressionError(ValueError):
    """Raised for any invalid, unsafe, or unevaluable expression."""


def _eval_node(node: ast.AST) -> float:
    """Recursively evaluate a single whitelisted AST node to a float.

    Args:
        node: An AST node produced by ``ast.parse(..., mode='eval')``.

    Returns:
        The numeric value of the node.

    Raises:
        ExpressionError: If the node type is not whitelisted or the
            computation itself fails (e.g. division by zero).
    """
    if isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float)):
            raise ExpressionError(
                f"Values of type '{type(node.value).__name__}' are not allowed; "
                "only numbers are supported."
            )
        return float(node.value)

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _BINARY_OPS:
            raise ExpressionError(
                f"Operator '{op_type.__name__}' is not supported. "
                "Allowed operators: +  -  *  /  //  %  **"
            )
        left: float = _eval_node(node.left)
        right: float = _eval_node(node.right)

        if op_type is ast.Pow and abs(right) > _MAX_EXPONENT:
            raise ExpressionError(
                f"Exponent {right} exceeds the maximum allowed value of {_MAX_EXPONENT}."
            )

        try:
            return _BINARY_OPS[op_type](left, right)
        except ZeroDivisionError:
            raise ExpressionError("Division by zero is undefined.")
        except OverflowError:
            raise ExpressionError("Result is too large to represent as a number.")

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _UNARY_OPS:
            raise ExpressionError(
                f"Unary operator '{op_type.__name__}' is not supported."
            )
        return _UNARY_OPS[op_type](_eval_node(node.operand))

    raise ExpressionError(
        f"'{type(node).__name__}' is not allowed. "
        "Only numeric expressions with +  -  *  /  //  %  ** and parentheses are supported."
    )


def evaluate(expression: str) -> float:
    """Parse and safely evaluate a mathematical expression string.

    Args:
        expression: A pre-validated, stripped expression string.

    Returns:
        The numeric result as a float.

    Raises:
        ExpressionError: If the expression contains a syntax error, an
            unsupported construct, or produces an invalid result.
    """
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        location = f" at position {exc.offset}" if exc.offset else ""
        raise ExpressionError(
            f"Syntax error{location}: {exc.msg}. "
            "Check for mismatched parentheses or invalid characters."
        ) from exc

    result: float = _eval_node(tree.body)

    if math.isnan(result):
        raise ExpressionError("Expression produced an undefined result (NaN).")
    if math.isinf(result):
        raise ExpressionError("Result overflows to infinity; try a smaller expression.")

    return result
