from datetime import datetime, timezone
from typing import Any

from utils.aggregators import aggregate_daily_intake


def format_clinician_report(user_id: str, events: list[Any], period_days: int) -> dict:
    daily_totals = aggregate_daily_intake(events)
    return {
        "user_id": user_id,
        "generated_at": datetime.now(timezone.utc),
        "period_days": period_days,
        "total_intake_ml": sum(daily_totals.values()),
        "event_count": len(events),
        "daily_totals_ml": daily_totals,
        "notes": (
            ["No fluid intake events were recorded for this period."]
            if not events
            else [f"Recorded fluid intake on {len(daily_totals)} day(s)."]
        ),
    }
