from enum import Enum


class JobQueueEntryStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"

    def __str__(self) -> str:
        return str(self.value)
