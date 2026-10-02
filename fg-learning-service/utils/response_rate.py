def compute_notification_response_rate(responses: int, notifications: int) -> float:
    if notifications == 0:
        return 0.0
    return round(responses / notifications, 3)
