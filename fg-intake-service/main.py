
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from fg_core.db.session import create_all
from fg_core.utils.cors import add_cors
from routers import barcode, image, manual, summary, text, payment


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all()
    yield


app = FastAPI(title="Intake Service", lifespan=lifespan)
add_cors(app)
app.include_router(text.router)
app.include_router(image.router)
app.include_router(barcode.router)
app.include_router(summary.router)
app.include_router(manual.router)
app.include_router(payment.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "intake"}
