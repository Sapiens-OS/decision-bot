from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class OutcomeDTO:
    """Outcome DTO"""

    id: int
    decision_id: int
    feedback: str
    score: int
    created_at: datetime
