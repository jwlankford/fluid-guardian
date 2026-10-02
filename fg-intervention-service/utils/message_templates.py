from models.decision import RiskLevel


_MESSAGES: dict[RiskLevel, str] = {
    "low": "Your fluid intake is within the expected range.",
    "moderate": "Please review your fluid intake and follow your care plan.",
    "high": "Your fluid intake may be elevated. Consider contacting your care team.",
    "critical": "Your fluid risk is critical. Contact your care team promptly.",
}


def render_message(risk_level: RiskLevel, user_name: str | None = None) -> str:
    greeting = f"Hello, {user_name}. " if user_name else ""
    return greeting + _MESSAGES[risk_level]
