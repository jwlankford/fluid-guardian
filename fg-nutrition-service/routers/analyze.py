from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from fg_core.db.session import get_session
from fg_core.models.fluid_event import FluidEvent
from models.hidden_fluid import EstimateRequest, HiddenFluidEstimate
from utils.hidden_fluid_rules import estimate_hidden_fluid_ml

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


@router.post("/estimate", response_model=HiddenFluidEstimate)
def estimate_hidden_fluid(request: EstimateRequest, db: Session = Depends(get_session)):
    event = db.get(FluidEvent, request.fluid_event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Fluid event not found")
    return HiddenFluidEstimate(
        fluid_event_id=event.id,
        hidden_fluid_ml=estimate_hidden_fluid_ml(event.event_type, event.payload),
        method="placeholder",
    )
