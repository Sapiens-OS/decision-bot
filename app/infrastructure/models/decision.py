from sqlalchemy import Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from enum import Enum as PyEnum
from app.infrastructure.models.base import Base
from ..utils.safe_enum import SafeEnumType


class DecisionStatus(PyEnum):
    """Decision status enum"""

    NEW = "new"
    DECIDED = "decided"
    COMPLETED = "completed"


class Decision(Base):
    """Decision model"""

    __tablename__ = "decisions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    problem: Mapped[str] = mapped_column(Text, nullable=False)
    analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    selected_option: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[DecisionStatus] = mapped_column(
        SafeEnumType(DecisionStatus), default=DecisionStatus.NEW, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="decisions")
    outcomes = relationship("Outcome", back_populates="decision", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Decision(id={self.id}, user_id={self.user_id}, status={self.status})>"
