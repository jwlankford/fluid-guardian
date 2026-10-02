def compute_risk(intake_ml: int, target_ml: int) -> tuple[str, float]:
    ratio = intake_ml / target_ml
    if ratio >= 1:
        return "critical", min(1.0, 0.75 + (ratio - 1) * 0.25)
    if ratio >= 0.8:
        return "high", 0.65
    if ratio >= 0.5:
        return "moderate", 0.4
    return "low", 0.15


def compute_probability(risk_score: float, hours_remaining: float) -> float:
    time_factor = min(1.0, max(0.0, hours_remaining / 24))
    return round(min(1.0, max(0.0, risk_score * (0.75 + 0.25 * time_factor))), 3)
