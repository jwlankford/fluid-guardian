Scaffold a FastAPI microservice called “Learning Service”.

Structure:
- main.py
- routers/
    - update.py (POST /learning/update)
    - profile.py (GET /learning/{user_id}/profile)
- models/
    - behavior_profile.py
- db/
    - base.py
    - session.py
- utils/
    - pattern_detection.py
    - response_rate.py
    - hotspot_analysis.py

Implement placeholder logic for:
- detect_evening_intake_pattern()
- compute_notification_response_rate()
- detect_risk_hotspots()

Use SQLAlchemy + Pydantic.  
Import shared models from fg-core.

# generate the scaffold
