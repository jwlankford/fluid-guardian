from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fg_core.db.session import get_session
from fg_core.models.fluid_event import FluidEvent
from fg_core.utils import utc_now
from models.fluid_event import ImageIntakeRequest, IntakeResponse, event_payload
from utils.image_classifier import classify_image

router = APIRouter(prefix="/intake", tags=["intake"])


@router.post("/image", response_model=IntakeResponse)
def intake_image(request: ImageIntakeRequest, db: Session = Depends(get_session)):
    result = classify_image(request.image_reference)
    event = FluidEvent(
        event_type="image_intake",
        occurred_at=utc_now(),
        payload=event_payload(request.user_id, result),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return {"event": event, "source": "image"}
