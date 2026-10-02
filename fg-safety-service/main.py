from contextlib import asynccontextmanager

from fastapi import FastAPI

from fg_core.db.session import create_all
from routers import evaluate, status


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all()
    yield


app = FastAPI(title="Safety Service", lifespan=lifespan)
app.include_router(evaluate.router)
app.include_router(status.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "safety"}
