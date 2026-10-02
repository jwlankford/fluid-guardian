Scaffold a FastAPI microservice called “Intake Service” with the following structure:

- main.py with FastAPI app and router includes
- routers/
    - text.py (POST /intake/text)
    - image.py (POST /intake/image)
    - barcode.py (POST /intake/barcode)
    - summary.py (GET /intake/{user_id}/today)
- models/
    - fluid_event.py (Pydantic + SQLAlchemy models)
- db/
    - base.py
    - session.py
- utils/
    - text_parser.py
    - image_classifier.py
    - barcode_lookup.py

Use SQLAlchemy + Pydantic.  
Use uvicorn entrypoint.  
Import shared models from fg-core when possible.  
Create placeholder functions for parsing, classification, and barcode lookup.

# generate the scaffold
