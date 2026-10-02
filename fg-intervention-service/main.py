from contextlib import asynccontextmanager

from fastapi import FastAPI

from fg_core.db.session import create_all
from fg_core.utils.cors import add_cors
from routers import act, decide, history


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all()
    yield


app = FastAPI(title="Intervention Service", lifespan=lifespan)
add_cors(app)
app.include_router(decide.router)
app.include_router(act.router)
app.include_router(history.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "intervention"}
