"""Escalation entity and validation schema."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from fg_core.db.base import Base
from fg_core.utils import generate_id, utc_now

EscalationStatus = Literal["open", "resolved", "dismissed"]


class Escalation(Base):
    __tablename__ = "escalations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_id)
    action_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )


class EscalationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_id)
    action_id: str | None = None
    level: int = Field(default=1, ge=1)
    reason: str = Field(min_length=1)
    status: EscalationStatus = "open"
    created_at: datetime = Field(default_factory=utc_now)
