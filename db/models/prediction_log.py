from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class PredictionLog(Base):
    """ORM model for storing prediction requests and results."""

    __tablename__ = "prediction_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid4()),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    crim: Mapped[float] = mapped_column(Float, nullable=False)
    zn: Mapped[float] = mapped_column(Float, nullable=False)
    indus: Mapped[float] = mapped_column(Float, nullable=False)
    chas: Mapped[int] = mapped_column(Integer, nullable=False)
    nox: Mapped[float] = mapped_column(Float, nullable=False)
    rm: Mapped[float] = mapped_column(Float, nullable=False)
    age: Mapped[float] = mapped_column(Float, nullable=False)
    dis: Mapped[float] = mapped_column(Float, nullable=False)
    rad: Mapped[int] = mapped_column(Integer, nullable=False)
    tax: Mapped[int] = mapped_column(Integer, nullable=False)
    ptratio: Mapped[float] = mapped_column(Float, nullable=False)
    black: Mapped[float] = mapped_column(Float, nullable=False)
    lstat: Mapped[float] = mapped_column(Float, nullable=False)

    predicted_medv: Mapped[float] = mapped_column(Float, nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")
    source: Mapped[str] = mapped_column(String(30), nullable=False, default="api")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="success")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
