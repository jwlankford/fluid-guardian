from datetime import datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from fg_core.db.session import get_session
from fg_core.models.fluid_event import FluidEvent
from fg_core.models.fluid_event import FluidEventSchema
from models.fluid_event import TodaySummary

router = APIRouter(prefix="/intake", tags=["intake"])


@router.get("/{user_id}/today", response_model=TodaySummary)
def get_today_summary(user_id: str, db: Session = Depends(get_session)):
    now = datetime.now(timezone.utc)
    start = datetime.combine(now.date(), time.min, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    events = db.scalars(
        select(FluidEvent)
        .where(FluidEvent.occurred_at >= start, FluidEvent.occurred_at < end)
        .order_by(FluidEvent.occurred_at)
    ).all()
    user_events = [
        event
        for event in events
        if event.payload.get("user_id") == user_id
    ]
    total = sum(
        int(event.payload["volume_ml"])
        for event in user_events
        if event.payload.get("volume_ml") is not None
    )
    return TodaySummary(
        user_id=user_id,
        date=start,
        total_fluid_ml=total,
        event_count=len(user_events),
        events=[FluidEventSchema.model_validate(event) for event in user_events],
    )
