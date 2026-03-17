"""Calculator route: POST /calculate."""

from fastapi import APIRouter, HTTPException

from app.models.calculator import CalculateRequest, CalculateResponse
from app.services import history as history_service
from app.services.calculator import ExpressionError, evaluate

router = APIRouter(prefix="/calculate", tags=["calculator"])


@router.post(
    "",
    response_model=CalculateResponse,
    status_code=200,
    summary="Evaluate an expression",
    response_description="The evaluated expression and its numeric result.",
)
def calculate(request: CalculateRequest) -> CalculateResponse:
    """Evaluate a mathematical expression and record it in the calculation history.

    - Supports: ``+``  ``-``  ``*``  ``/``  ``//``  ``%``  ``**`` and parentheses.
    - Rejects: function calls, variable names, and any non-numeric construct.

    Returns **422 Unprocessable Entity** for invalid or unsafe expressions.
    """
    try:
        result: float = evaluate(request.expression)
    except ExpressionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    history_service.record(request.expression, result)
    return CalculateResponse(expression=request.expression, result=result)
