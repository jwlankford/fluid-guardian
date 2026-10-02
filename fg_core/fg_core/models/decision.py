"""Decision entity and validation schema."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from fg_core.db.base import Base
from fg_core.utils import generate_id, utc_now


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_id)
    prediction_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    decision: Mapped[str] = mapped_column(String(100), nullable=False)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)


class DecisionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_id)
    prediction_id: str | None = None
    decided_at: datetime = Field(default_factory=utc_now)
    decision: str = Field(min_length=1, max_length=100)
    rationale: str | None = None
