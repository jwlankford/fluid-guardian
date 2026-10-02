def identify_drivers(
    intake_ml: int, target_ml: int, intake_rate_ml_per_hour: float
) -> list[str]:
    drivers: list[str] = []
    if intake_ml >= target_ml:
        drivers.append("intake_at_or_above_target")
    elif intake_ml >= target_ml * 0.8:
        drivers.append("intake_near_target")
    if intake_rate_ml_per_hour > 0:
        drivers.append("ongoing_intake")
    if not drivers:
        drivers.append("no_elevated_intake_driver_identified")
    return drivers
