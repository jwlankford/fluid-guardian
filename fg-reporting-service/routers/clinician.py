from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from fg_core.db.session import get_session
from models.report import ClinicianReport
from routers._shared import get_user_events, utc_day_range
from utils.clinician_formatter import format_clinician_report

router = APIRouter(prefix="/report", tags=["reporting"])


@router.get("/clinician/{user_id}", response_model=ClinicianReport)
def get_clinician_report(
    user_id: str,
    period_days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_session),
):
    start, end = utc_day_range(period_days)
    events = get_user_events(db, user_id, start, end)
    return format_clinician_report(user_id, events, period_days)
