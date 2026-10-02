"""Shared CORS configuration for the Fluid Guardian APIs."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

DEFAULT_ORIGINS = (
    "http://localhost:5173,"
    "https://fluid-guardian-frontend.onrender.com,"
    "https://jwlankford.github.io"
)


def add_cors(app: FastAPI) -> None:
    """Allow browser clients listed in the comma-separated FG_CORS_ORIGINS."""
    origins = [o.strip() for o in os.getenv("FG_CORS_ORIGINS", DEFAULT_ORIGINS).split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
