"""Prediction entity and validation schema."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DateTime, Float, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from fg_core.db.base import Base
from fg_core.utils import generate_id, utc_now


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_id)
    fluid_event_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    predicted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    outcome: Mapped[str] = mapped_column(String(200), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)


class PredictionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_id)
    fluid_event_id: str | None = None
    predicted_at: datetime = Field(default_factory=utc_now)
    outcome: str = Field(min_length=1, max_length=200)
    confidence: float = Field(ge=0, le=1)
    details: dict[str, Any] = Field(default_factory=dict)
