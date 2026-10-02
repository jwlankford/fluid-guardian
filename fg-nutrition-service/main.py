Scaffold a FastAPI microservice called “Nutrition Service” for hidden fluid analysis.

Structure:
- main.py
- routers/
    - analyze.py (POST /nutrition/estimate)
- models/
    - hidden_fluid.py
- db/
    - base.py
    - session.py
- utils/
    - hidden_fluid_rules.py
    - food_lookup.py

Implement endpoint that accepts a fluid_event_id and returns hidden_fluid_ml.  
Use placeholder logic for hidden fluid estimation.  
Use SQLAlchemy + Pydantic.  
Import shared models from fg-core.

# generate the scaffold
