Scaffold a FastAPI microservice called “Intervention Service”.

Structure:
- main.py
- routers/
    - decide.py (POST /intervention/decide)
    - act.py (POST /intervention/act)
    - history.py (GET /intervention/{user_id}/history)
- models/
    - decision.py
    - action.py
- db/
    - base.py
    - session.py
- utils/
    - message_templates.py
    - delivery.py

Implement placeholder decision logic based on risk_level.  
Implement placeholder message rendering.  
Use SQLAlchemy + Pydantic.  
Import shared models from fg-core.

# generate the scaffold


