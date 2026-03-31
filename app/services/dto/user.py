from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class UserDTO:
    """User DTO"""

    id: int
    telegram_id: int
    username: str | None
    max_questions: int
    created_at: datetime
