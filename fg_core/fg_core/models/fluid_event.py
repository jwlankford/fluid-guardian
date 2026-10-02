"""Fluid event entity and validation schema."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DateTime, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from fg_core.db.base import Base
from fg_core.utils import generate_id, utc_now


class FluidEvent(Base):
    __tablename__ = "fluid_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_id)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)


class FluidEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_id)
    event_type: str = Field(min_length=1, max_length=100)
    occurred_at: datetime = Field(default_factory=utc_now)
    payload: dict[str, Any] = Field(default_factory=dict)
