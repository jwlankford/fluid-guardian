Scaffold a FastAPI microservice called “Reporting Service”.

Structure:
- main.py
- routers/
    - daily.py (GET /report/daily/{user_id})
    - weekly.py (GET /report/weekly/{user_id})
    - clinician.py (GET /report/clinician/{user_id})
- models/
    - report.py
- db/
    - base.py
    - session.py
- utils/
    - aggregators.py
    - summarizers.py
    - clinician_formatter.py

Implement placeholder aggregation logic for:
- daily intake
- weekly summaries
- clinician reports

Use SQLAlchemy + Pydantic.  
Import shared models from fg-core.

# generate the scaffold
