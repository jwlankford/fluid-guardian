from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from fg_core.models.fluid_event import FluidEvent


def get_user_events(
    db: Session, user_id: str, start: datetime, end: datetime
) -> list[FluidEvent]:
    events = db.scalars(
        select(FluidEvent)
        .where(FluidEvent.occurred_at >= start, FluidEvent.occurred_at < end)
        .order_by(FluidEvent.occurred_at)
    ).all()
    return [event for event in events if event.payload.get("user_id") == user_id]


def utc_day_range(days: int) -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)
    end = datetime.combine(now.date() + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)
    return end - timedelta(days=days), end
