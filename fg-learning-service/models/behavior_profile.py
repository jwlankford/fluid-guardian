from typing import Any

from pydantic import BaseModel, Field

from fg_core.models.behavior_profile import BehaviorProfile, BehaviorProfileSchema


class LearningUpdateRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=200)
    recent_events: list[dict[str, Any]] = Field(default_factory=list)
    notification_count: int = Field(default=0, ge=0)
    notification_responses: int = Field(default=0, ge=0)


class LearningUpdateResponse(BaseModel):
    profile: BehaviorProfileSchema
    evening_intake_pattern: bool
    notification_response_rate: float
    risk_hotspots: list[str]


__all__ = [
    "BehaviorProfile",
    "BehaviorProfileSchema",
    "LearningUpdateRequest",
    "LearningUpdateResponse",
]
