from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fg_core.db.session import get_session
from fg_core.models.prediction import Prediction
from fg_core.utils import utc_now
from models.prediction import PredictRequest, PredictResponse
from utils.behavior_adjustments import identify_drivers
from utils.risk_engine import compute_probability, compute_risk
from utils.time_projection import estimate_exceed_time

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post("/daily", response_model=PredictResponse)
def predict_daily(request: PredictRequest, db: Session = Depends(get_session)):
    risk_level, risk_score = compute_risk(request.intake_ml, request.target_ml)
    probability = compute_probability(risk_score, request.hours_remaining)
    exceed_time = estimate_exceed_time(
        request.intake_ml, request.target_ml, request.intake_rate_ml_per_hour
    )
    drivers = identify_drivers(
        request.intake_ml, request.target_ml, request.intake_rate_ml_per_hour
    )
    prediction = Prediction(
        predicted_at=utc_now(),
        outcome=risk_level,
        confidence=probability,
        details={
            "user_id": request.user_id,
            "risk_score": risk_score,
            "intake_ml": request.intake_ml,
            "target_ml": request.target_ml,
            "hours_remaining": request.hours_remaining,
            "estimated_exceed_time_hours": exceed_time,
            "drivers": drivers,
        },
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return PredictResponse(
        prediction=prediction,
        risk_level=risk_level,
        probability=probability,
        estimated_exceed_time_hours=exceed_time,
        drivers=drivers,
    )
