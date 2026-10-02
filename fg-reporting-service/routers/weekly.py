from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fg_core.db.session import get_session
from models.report import WeeklyReport
from routers._shared import get_user_events, utc_day_range
from utils.aggregators import aggregate_daily_intake

router = APIRouter(prefix="/report", tags=["reporting"])


@router.get("/weekly/{user_id}", response_model=WeeklyReport)
def get_weekly_report(user_id: str, db: Session = Depends(get_session)):
    start, end = utc_day_range(7)
    events = get_user_events(db, user_id, start, end)
    daily_totals = aggregate_daily_intake(events)
    return WeeklyReport(
        user_id=user_id,
        start_date=start.date(),
        end_date=(end - timedelta(days=1)).date(),
        daily_totals_ml=daily_totals,
        total_intake_ml=sum(daily_totals.values()),
        event_count=len(events),
    )
