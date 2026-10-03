from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from fg_core.db.base import Base
from fg_core.utils import generate_id


class UserAccount(Base):
    __tablename__ = "user_accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_id)
    user_id: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    credits: Mapped[int] = mapped_column(Integer, nullable=False, default=3)


class UserAccountSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=generate_id)
    user_id: str = Field(min_length=1, max_length=200)
    credits: int = Field(default=3, ge=0)
