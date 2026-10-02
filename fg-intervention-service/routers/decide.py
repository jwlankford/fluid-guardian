from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fg_core.db.session import get_session
from fg_core.models.decision import Decision
from models.decision import DecideRequest, DecisionResponse
from utils.message_templates import render_message

router = APIRouter(prefix="/intervention", tags=["intervention"])


def decide_for_risk(risk_level: str) -> tuple[str, str]:
    if risk_level == "critical":
        return "urgent_outreach", "Critical risk requires prompt care-team contact."
    if risk_level == "high":
        return "send_alert", "High risk warrants a care-team alert."
    if risk_level == "moderate":
        return "send_reminder", "Moderate risk warrants a supportive reminder."
    return "monitor", "Low risk; continue monitoring."


@router.post("/decide", response_model=DecisionResponse)
def create_decision(request: DecideRequest, db: Session = Depends(get_session)):
    decision_text, rationale = decide_for_risk(request.risk_level)
    decision = Decision(
        prediction_id=request.prediction_id,
        decision=decision_text,
        rationale=rationale,
    )
    db.add(decision)
    db.commit()
    db.refresh(decision)
    return DecisionResponse(
        decision=decision,
        recommendation=render_message(request.risk_level),
    )
