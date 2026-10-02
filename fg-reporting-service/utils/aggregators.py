from datetime import date
from typing import Any


def aggregate_daily_intake(events: list[Any]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for event in events:
        event_date = event.occurred_at.date().isoformat()
        volume_ml = event.payload.get("volume_ml")
        totals[event_date] = totals.get(event_date, 0) + (
            int(volume_ml) if volume_ml is not None else 0
        )
    return totals


def daily_intake(events: list[Any], report_date: date) -> int:
    return aggregate_daily_intake(events).get(report_date.isoformat(), 0)
