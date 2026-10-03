from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from fg_core.models.fluid_event import FluidEvent


def get_user_events(
    db: Session,
    user_id: str,
    start: datetime | None = None,
    end: datetime | None = None,
) -> list[FluidEvent]:
    query = select(FluidEvent)
    if start is not None:
        query = query.where(FluidEvent.occurred_at >= start)
    if end is not None:
        query = query.where(FluidEvent.occurred_at < end)
    query = query.order_by(FluidEvent.occurred_at)

    events = db.scalars(query).all()
    return [
        event 
        for event in events 
        if event.payload.get("user_id") == user_id
    ]


def utc_day_range(days: int) -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)
    end = datetime.combine(now.date() + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)
    return end - timedelta(days=days), end
