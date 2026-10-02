def deliver_message(message: str, channel: str = "in_app") -> dict[str, str]:
    """Placeholder delivery adapter; no external notification provider is configured."""
    return {"status": "not_configured", "channel": channel, "message": message}
