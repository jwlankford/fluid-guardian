from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from fg_core.db.session import get_session
from models.report import PeriodDayData, PeriodReport
from routers._shared import get_user_events

router = APIRouter(prefix="/report", tags=["reporting"])


@router.get("/period/{user_id}", response_model=PeriodReport)
def get_period_report(
    user_id: str,
    start_date: date | None = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end_date: date | None = Query(default=None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_session),
):
    now = datetime.now(timezone.utc)
    if end_date is None:
        end_date = now.date()
    if start_date is None:
        start_date = end_date - timedelta(days=6)

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    start_dt = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
    end_dt = datetime.combine(end_date + timedelta(days=1), time.min, tzinfo=timezone.utc)

    events = get_user_events(db, user_id, start_dt, end_dt)

    events_by_date: dict[date, list] = defaultdict(list)
    for event in events:
        event_d = event.occurred_at.date()
        events_by_date[event_d].append(event)

    days: list[PeriodDayData] = []
    daily_totals: dict[str, int] = {}
    running_totals: dict[str, int] = {}

    running_sum = 0
    curr = start_date
    while curr <= end_date:
        day_events = events_by_date.get(curr, [])
        day_volume = sum(
            int(e.payload.get("volume_ml", 0))
            for e in day_events
            if e.payload.get("volume_ml") is not None
        )
        running_sum += day_volume
        iso_str = curr.isoformat()
        daily_totals[iso_str] = day_volume
        running_totals[iso_str] = running_sum

        days.append(
            PeriodDayData(
                date=curr,
                intake_ml=day_volume,
                running_intake_ml=running_sum,
                event_count=len(day_events),
            )
        )
        curr += timedelta(days=1)

    total_intake = running_sum
    num_days = max(len(days), 1)
    average_daily = round(total_intake / num_days, 1)

    return PeriodReport(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        total_intake_ml=total_intake,
        average_daily_ml=average_daily,
        event_count=len(events),
        daily_totals_ml=daily_totals,
        running_totals_ml=running_totals,
        days=days,
    )
