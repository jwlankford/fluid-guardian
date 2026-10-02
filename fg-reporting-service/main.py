from contextlib import asynccontextmanager

from fastapi import FastAPI

from fg_core.db.session import create_all
from routers import clinician, daily, weekly


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all()
    yield


app = FastAPI(title="Reporting Service", lifespan=lifespan)
app.include_router(daily.router)
app.include_router(weekly.router)
app.include_router(clinician.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "reporting"}
