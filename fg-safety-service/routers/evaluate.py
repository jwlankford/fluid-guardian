from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fg_core.db.session import get_session
from fg_core.models.escalation import Escalation
from models.escalation import EvaluateRequest, EvaluationResponse
from utils.escalation_logic import get_escalation_level
from utils.red_flag_rules import detect_red_flags
from utils.symptom_scoring import score_symptoms

router = APIRouter(prefix="/safety", tags=["safety"])


@router.post("/evaluate", response_model=EvaluationResponse)
def evaluate_safety(request: EvaluateRequest, db: Session = Depends(get_session)):
    red_flags = detect_red_flags(request.symptoms)
    risk_score = score_symptoms(request.symptoms, red_flags)
    level = get_escalation_level(risk_score)
    escalation = None
    if level is not None:
        reasons = ", ".join(red_flags) or "multiple reported symptoms"
        escalation = Escalation(
            level=level,
            reason=f"[user:{request.user_id}] {reasons}",
            status="open",
        )
        db.add(escalation)
        db.commit()
        db.refresh(escalation)
    recommendation = (
        "Potential emergency symptoms detected. Seek urgent medical help now."
        if red_flags
        else "No configured red flags were detected; follow the user's care plan."
    )
    return EvaluationResponse(
        user_id=request.user_id,
        red_flags=red_flags,
        risk_score=risk_score,
        escalation=escalation,
        recommendation=recommendation,
    )
