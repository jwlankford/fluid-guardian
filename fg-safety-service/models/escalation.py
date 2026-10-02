from pydantic import BaseModel, Field

from fg_core.models.escalation import Escalation, EscalationSchema


class EvaluateRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=200)
    symptoms: list[str] = Field(default_factory=list)


class EvaluationResponse(BaseModel):
    user_id: str
    red_flags: list[str]
    risk_score: int
    escalation: EscalationSchema | None
    recommendation: str


class SafetyStatus(BaseModel):
    user_id: str
    status: str
    escalations: list[EscalationSchema]


__all__ = [
    "Escalation",
    "EscalationSchema",
    "EvaluateRequest",
    "EvaluationResponse",
    "SafetyStatus",
]
