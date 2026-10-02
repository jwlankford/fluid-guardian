from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fg_core.db.session import get_session
from fg_core.models.fluid_event import FluidEvent
from fg_core.utils import utc_now
from models.fluid_event import IntakeResponse, TextIntakeRequest, event_payload
from utils.text_parser import parse_fluid_text

router = APIRouter(prefix="/intake", tags=["intake"])


@router.post("/text", response_model=IntakeResponse)
def intake_text(request: TextIntakeRequest, db: Session = Depends(get_session)):
    volume_ml, normalized_text = parse_fluid_text(request.text)
    event = FluidEvent(
        event_type="text_intake",
        occurred_at=utc_now(),
        payload=event_payload(
            request.user_id, {"text": normalized_text, "volume_ml": volume_ml}
        ),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return IntakeResponse(
        event=event,
        recognized_volume_ml=volume_ml,
        source="text",
    )
