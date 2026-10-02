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

## Deploy APIs with Neon and Render

The Render Blueprint in `render.yaml` defines all seven FastAPI services.
They share a Neon PostgreSQL database through the `FG_DATABASE_URL` environment
variable. The value is intentionally not stored in this repository.

1. Create a PostgreSQL project in [Neon](https://console.neon.tech/). In
   **Connect**, select the pooled connection string and copy its URI. Keep it
   secret; it includes the database password.
2. Push this repository to GitHub, then in [Render](https://dashboard.render.com/)
   create a **Blueprint** and select the repository. Render discovers
   `render.yaml` and creates the seven API services.
3. Set each service's `FG_DATABASE_URL` to the Neon URI in Render's environment
   settings. Use the same URI for all seven services; do not commit it or put it
   in source control. SQLAlchemy accepts Neon's `postgresql://` URI directly.
4. Wait for each deployment to finish and check its `/health` endpoint. The
   Render service URL is shown on that service's page; its API docs are at
   `/docs`.

The Blueprint uses Render's free instance plan to avoid provisioning paid
resources automatically. Free web services can spin down when idle, so expect
cold starts; select a paid plan in Render if the APIs need to stay warm.
