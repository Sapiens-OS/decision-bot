from sqlalchemy import Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.infrastructure.models.base import Base


class Outcome(Base):
    """Outcome model"""

    __tablename__ = "outcomes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    decision_id: Mapped[int] = mapped_column(Integer, ForeignKey("decisions.id"), nullable=False, index=True)
    feedback: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)  # -2 to +2
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    decision: Mapped["Decision"] = relationship("Decision", back_populates="outcomes")

    def __repr__(self):
        return f"<Outcome(id={self.id}, decision_id={self.decision_id}, score={self.score})>"
