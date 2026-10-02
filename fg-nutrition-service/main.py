from contextlib import asynccontextmanager

from fastapi import FastAPI

from fg_core.db.session import create_all
from routers import analyze


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all()
    yield


app = FastAPI(title="Nutrition Service", lifespan=lifespan)
app.include_router(analyze.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "nutrition"}
