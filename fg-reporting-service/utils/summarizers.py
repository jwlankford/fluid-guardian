from typing import Any

from utils.aggregators import aggregate_daily_intake


def summarize_weekly(events: list[Any]) -> dict[str, int]:
    return aggregate_daily_intake(events)


def summarize_clinician(events: list[Any]) -> list[str]:
    totals = aggregate_daily_intake(events)
    if not totals:
        return ["No fluid intake events were recorded for this period."]
    return [f"Recorded fluid intake on {len(totals)} day(s)."]
