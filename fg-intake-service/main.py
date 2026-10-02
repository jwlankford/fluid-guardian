import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from contextlib import asynccontextmanager

from fastapi import FastAPI

from fg_core.fg_core.db.session import create_all
from routers import barcode, image, summary, text


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all()
    yield


app = FastAPI(title="Intake Service", lifespan=lifespan)
app.include_router(text.router)
app.include_router(image.router)
app.include_router(barcode.router)
app.include_router(summary.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "intake"}
