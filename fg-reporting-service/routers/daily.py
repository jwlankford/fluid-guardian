from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fg_core.db.session import get_session
from fg_core.models.fluid_event import FluidEventSchema
from models.report import DailyReport
from routers._shared import get_user_events
from utils.aggregators import daily_intake

router = APIRouter(prefix="/report", tags=["reporting"])


@router.get("/daily/{user_id}", response_model=DailyReport)
def get_daily_report(
    user_id: str,
    report_date: date | None = None,
    db: Session = Depends(get_session),
):
    target_date = report_date or datetime.now(timezone.utc).date()
    start = datetime.combine(target_date, time.min, tzinfo=timezone.utc)
    events = get_user_events(db, user_id, start, start + timedelta(days=1))
    return DailyReport(
        user_id=user_id,
        date=target_date,
        total_intake_ml=daily_intake(events, target_date),
        event_count=len(events),
        events=[FluidEventSchema.model_validate(event) for event in events],
    )
