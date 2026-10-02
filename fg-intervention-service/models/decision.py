from typing import Literal

from pydantic import BaseModel, Field

from fg_core.models.decision import Decision, DecisionSchema

RiskLevel = Literal["low", "moderate", "high", "critical"]


class DecideRequest(BaseModel):
    risk_level: RiskLevel
    prediction_id: str | None = None


class DecisionResponse(BaseModel):
    decision: DecisionSchema
    recommendation: str


__all__ = [
    "DecideRequest",
    "Decision",
    "DecisionResponse",
    "DecisionSchema",
    "RiskLevel",
]
