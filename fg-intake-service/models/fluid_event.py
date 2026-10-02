from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from fg_core.models.fluid_event import FluidEvent, FluidEventSchema


class IntakeRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=200)


class TextIntakeRequest(IntakeRequest):
    text: str = Field(min_length=1)


class ImageIntakeRequest(IntakeRequest):
    image_reference: str = Field(min_length=1)


class BarcodeIntakeRequest(IntakeRequest):
    barcode: str = Field(min_length=1, max_length=100)
    volume_ml: int | None = Field(default=None, gt=0)


class IntakeResponse(BaseModel):
    event: FluidEventSchema
    recognized_volume_ml: int | None = None
    source: str


class TodaySummary(BaseModel):
    user_id: str
    date: datetime
    total_fluid_ml: int
    event_count: int
    events: list[FluidEventSchema]


def event_payload(user_id: str, data: dict[str, Any]) -> dict[str, Any]:
    return {"user_id": user_id, **data}


__all__ = [
    "BarcodeIntakeRequest",
    "FluidEvent",
    "FluidEventSchema",
    "ImageIntakeRequest",
    "IntakeResponse",
    "TextIntakeRequest",
    "TodaySummary",
    "event_payload",
]
