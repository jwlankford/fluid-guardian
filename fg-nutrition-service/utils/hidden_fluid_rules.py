def estimate_hidden_fluid_ml(event_type: str, payload: dict) -> int:
    """Return an explicit placeholder estimate until food rules are configured."""
    explicit_value = payload.get("hidden_fluid_ml")
    if isinstance(explicit_value, int) and explicit_value >= 0:
        return explicit_value
    return 0
