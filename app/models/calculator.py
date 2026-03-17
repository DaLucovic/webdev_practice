"""Pydantic models for the calculator and history endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CalculateRequest(BaseModel):
    """Request body for POST /calculate."""

    expression: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="Mathematical expression to evaluate.",
        examples=["2 + 3 * (10 / 2)"],
    )

    @field_validator("expression")
    @classmethod
    def strip_and_validate(cls, v: str) -> str:
        """Strip surrounding whitespace; reject whitespace-only strings."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Expression must not be empty or whitespace only.")
        return stripped


class CalculateResponse(BaseModel):
    """Successful calculation result."""

    expression: str = Field(..., description="The expression that was evaluated.")
    result: float = Field(..., description="Numeric result of the expression.")


class HistoryEntry(BaseModel):
    """A single recorded calculation."""

    expression: str = Field(..., description="The expression that was evaluated.")
    result: float = Field(..., description="Numeric result of the expression.")
    timestamp: datetime = Field(
        ..., description="UTC timestamp when the calculation was performed."
    )


class ClearHistoryResponse(BaseModel):
    """Response returned after clearing the calculation history."""

    deleted: int = Field(
        ..., ge=0, description="Number of history entries that were removed."
    )
