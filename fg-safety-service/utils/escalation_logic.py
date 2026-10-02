def get_escalation_level(risk_score: int) -> int | None:
    if risk_score >= 80:
        return 3
    if risk_score >= 40:
        return 2
    return None
