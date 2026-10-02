from contextlib import asynccontextmanager

from fastapi import FastAPI

from fg_core.db.session import create_all
from routers import history, predict


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all()
    yield


app = FastAPI(title="Prediction Service", lifespan=lifespan)
app.include_router(predict.router)
app.include_router(history.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "prediction"}
