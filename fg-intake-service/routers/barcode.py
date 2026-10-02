from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fg_core.db.session import get_session
from fg_core.models.fluid_event import FluidEvent
from fg_core.utils import utc_now
from models.fluid_event import BarcodeIntakeRequest, IntakeResponse, event_payload
from utils.barcode_lookup import lookup_barcode

router = APIRouter(prefix="/intake", tags=["intake"])


@router.post("/barcode", response_model=IntakeResponse)
def intake_barcode(request: BarcodeIntakeRequest, db: Session = Depends(get_session)):
    product = lookup_barcode(request.barcode)
    volume_ml = request.volume_ml or product["volume_ml"]
    event = FluidEvent(
        event_type="barcode_intake",
        occurred_at=utc_now(),
        payload=event_payload(
            request.user_id,
            {**product, "volume_ml": volume_ml},
        ),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return IntakeResponse(
        event=event,
        recognized_volume_ml=volume_ml,
        source="barcode",
    )
