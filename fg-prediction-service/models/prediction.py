from pydantic import BaseModel, Field

from fg_core.models.prediction import Prediction, PredictionSchema


class PredictRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=200)
    intake_ml: int = Field(ge=0)
    target_ml: int = Field(gt=0)
    hours_remaining: float = Field(default=24, gt=0, le=168)
    intake_rate_ml_per_hour: float = Field(default=0, ge=0)


class PredictResponse(BaseModel):
    prediction: PredictionSchema
    risk_level: str
    probability: float
    estimated_exceed_time_hours: float | None
    drivers: list[str]


__all__ = ["Prediction", "PredictionSchema", "PredictRequest", "PredictResponse"]
