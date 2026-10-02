from typing import Any


def detect_risk_hotspots(events: list[dict[str, Any]]) -> list[str]:
    hotspots: set[str] = set()
    for event in events:
        if event.get("risk_level") in {"high", "critical"}:
            hour = event.get("hour")
            if isinstance(hour, int) and 0 <= hour <= 23:
                hotspots.add(f"hour_{hour:02d}")
    return sorted(hotspots)
