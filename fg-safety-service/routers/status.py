from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from fg_core.db.session import get_session
from fg_core.models.escalation import Escalation
from fg_core.models.escalation import EscalationSchema
from models.escalation import SafetyStatus

router = APIRouter(prefix="/safety", tags=["safety"])


@router.get("/{user_id}/status", response_model=SafetyStatus)
def get_safety_status(user_id: str, db: Session = Depends(get_session)):
    escalations = db.scalars(
        select(Escalation).where(Escalation.status == "open").order_by(Escalation.created_at.desc())
    ).all()
    user_escalations = [
        escalation
        for escalation in escalations
        if escalation.reason.startswith(f"[user:{user_id}] ")
    ]
    return SafetyStatus(
        user_id=user_id,
        status="open" if user_escalations else "clear",
        escalations=[EscalationSchema.model_validate(item) for item in user_escalations],
    )
