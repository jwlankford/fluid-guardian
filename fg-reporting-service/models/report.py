from datetime import date, datetime

from pydantic import BaseModel

from fg_core.models.fluid_event import FluidEventSchema


class DailyReport(BaseModel):
    user_id: str
    date: date
    total_intake_ml: int
    event_count: int
    events: list[FluidEventSchema]


class WeeklyReport(BaseModel):
    user_id: str
    start_date: date
    end_date: date
    daily_totals_ml: dict[str, int]
    total_intake_ml: int
    event_count: int


class ClinicianReport(BaseModel):
    user_id: str
    generated_at: datetime
    period_days: int
    total_intake_ml: int
    event_count: int
    daily_totals_ml: dict[str, int]
    notes: list[str]


class PeriodDayData(BaseModel):
    date: date
    intake_ml: int
    running_intake_ml: int
    event_count: int


class PeriodReport(BaseModel):
    user_id: str
    start_date: date
    end_date: date
    total_intake_ml: int
    average_daily_ml: float
    event_count: int
    daily_totals_ml: dict[str, int]
    running_totals_ml: dict[str, int]
    days: list[PeriodDayData]

