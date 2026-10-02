"""Behavior profile entity and validation schema."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DateTime, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from fg_core.db.base import Base
from fg_core.utils import generate_id, utc_now


class BehaviorProfile(Base):
    __tablename__ = "behavior_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_id)
    subject_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    profile: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )


class BehaviorProfileSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_id)
    subject_id: str = Field(min_length=1, max_length=200)
    profile: dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=utc_now)
