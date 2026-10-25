from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Session:
    subject: str
    target_seconds: float
    started_at: datetime | None = None
    finished_at: datetime | None = None
    actual_seconds: float = 0.0
    paused_seconds: float = 0.0
    completed: bool = False
    pauses: list[dict] = field(default_factory=list)
