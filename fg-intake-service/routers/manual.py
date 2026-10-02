from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from fg_core.db.session import get_session
from fg_core.models.fluid_event import FluidEvent
from fg_core.utils import utc_now
from models.fluid_event import IntakeResponse, event_payload

router = APIRouter(prefix="/intake", tags=["intake"])

class ManualIntakeRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=200)
    volume_ml: int = Field(gt=0)

@router.post("/manual", response_model=IntakeResponse)
def intake_manual(request: ManualIntakeRequest, db: Session = Depends(get_session)):
    event = FluidEvent(
        event_type="manual_intake",
        occurred_at=utc_now(),
        payload=event_payload(
            request.user_id, {"volume_ml": request.volume_ml}
        ),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return IntakeResponse(
        event=event,
        recognized_volume_ml=request.volume_ml,
        source="manual",
    )
