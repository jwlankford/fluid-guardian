def estimate_exceed_time(
    intake_ml: int, target_ml: int, intake_rate_ml_per_hour: float
) -> float | None:
    if intake_ml >= target_ml:
        return 0.0
    if intake_rate_ml_per_hour <= 0:
        return None
    return round((target_ml - intake_ml) / intake_rate_ml_per_hour, 2)
