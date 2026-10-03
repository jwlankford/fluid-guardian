from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from fg_core.db.session import create_all
from fg_core.utils.cors import add_cors
from routers import clinician, daily, period, weekly


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all()
    yield


app = FastAPI(title="Reporting Service", lifespan=lifespan)
add_cors(app)
app.include_router(daily.router)
app.include_router(weekly.router)
app.include_router(clinician.router)
app.include_router(period.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "reporting"}
