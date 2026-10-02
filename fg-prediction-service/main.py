Scaffold a FastAPI microservice called “Prediction Service”.

Structure:
- main.py
- routers/
    - predict.py (POST /predict/daily)
    - history.py (GET /predict/{user_id}/history)
- models/
    - prediction.py
- db/
    - base.py
    - session.py
- utils/
    - risk_engine.py
    - time_projection.py
    - behavior_adjustments.py

Implement placeholder risk logic:
- compute_risk()
- compute_probability()
- estimate_exceed_time()
- identify_drivers()

Use SQLAlchemy + Pydantic.  
Import shared models from fg-core.

# generate the scaffold

