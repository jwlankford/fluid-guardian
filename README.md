# Fluid Guardian

The repository contains shared Python entities in `fg-core`, seven FastAPI
services, and a Vue frontend. The service endpoints and domain helpers are
initial scaffolds; image classification, product lookup, notification delivery,
and clinical decision rules are placeholders and are not production integrations.

## Run a service locally

Use Python 3.10 or newer. From the repository root, install the shared package
and the requirements for the service you want to run:

```powershell
python -m pip install -e .\fg-core
python -m pip install -r .\fg-intake-service\requirements.txt
python -m uvicorn main:app --app-dir .\fg-intake-service --reload
```

Replace `fg-intake-service` with `fg-intervention-service`,
`fg-learning-service`, `fg-nutrition-service`, `fg-prediction-service`,
`fg-reporting-service`, or `fg-safety-service` to run another service.
Each API exposes `/health` and its interactive OpenAPI docs at `/docs`.

Services use the shared `FG_DATABASE_URL` setting, which defaults to a local
SQLite database named `fg_core.db` in the server's working directory.
