from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from fg_core.db.session import get_session
from fg_core.models.prediction import Prediction, PredictionSchema

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.get("/{user_id}/history", response_model=list[PredictionSchema])
def get_prediction_history(user_id: str, db: Session = Depends(get_session)):
    predictions = db.scalars(
        select(Prediction).order_by(Prediction.predicted_at.desc())
    ).all()
    return [
        prediction
        for prediction in predictions
        if prediction.details.get("user_id") == user_id
    ]
