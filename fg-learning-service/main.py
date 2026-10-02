from contextlib import asynccontextmanager

from fastapi import FastAPI

from fg_core.db.session import create_all
from routers import profile, update


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all()
    yield


app = FastAPI(title="Learning Service", lifespan=lifespan)
app.include_router(update.router)
app.include_router(profile.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "learning"}
