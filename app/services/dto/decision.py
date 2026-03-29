from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class DecisionStatus(Enum):
    """Decision status enum"""

    NEW = "new"
    DECIDED = "decided"
    COMPLETED = "completed"


@dataclass(frozen=True)
class DecisionDTO:
    """Decision DTO"""

    id: int
    user_id: int
    problem: str
    analysis: str | None
    selected_option: str | None
    status: DecisionStatus
    created_at: datetime
    user_telegram_id: int | None = None
