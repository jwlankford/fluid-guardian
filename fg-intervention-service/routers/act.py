from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fg_core.db.session import get_session
from fg_core.models.action import Action
from models.action import ActRequest, ActionResponse
from utils.delivery import deliver_message

router = APIRouter(prefix="/intervention", tags=["intervention"])


@router.post("/act", response_model=ActionResponse)
def create_action(request: ActRequest, db: Session = Depends(get_session)):
    action = Action(
        decision_id=request.decision_id,
        action_type=request.action_type,
        status="pending",
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    delivery = deliver_message(request.action_type)
    return ActionResponse(action=action, message=delivery["status"])
