from enum import StrEnum


class JobQueueEntryStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"

    def __str__(self) -> str:
        return str(self.value)
