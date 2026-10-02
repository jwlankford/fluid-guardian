from typing import Any


def detect_evening_intake_pattern(events: list[dict[str, Any]]) -> bool:
    evening_events = 0
    for event in events:
        hour = event.get("hour")
        if isinstance(hour, int) and 18 <= hour <= 23:
            evening_events += 1
    return evening_events >= 2
