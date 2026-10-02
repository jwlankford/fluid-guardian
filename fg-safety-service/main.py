Scaffold a FastAPI microservice called “Safety Service”.

Structure:
- main.py
- routers/
    - evaluate.py (POST /safety/evaluate)
    - status.py (GET /safety/{user_id}/status)
- models/
    - escalation.py
- db/
    - base.py
    - session.py
- utils/
    - red_flag_rules.py
    - symptom_scoring.py
    - escalation_logic.py

Implement placeholder red-flag detection and escalation logic.  
Use SQLAlchemy + Pydantic.  
Import shared models from fg-core.

# generate the scaffold
