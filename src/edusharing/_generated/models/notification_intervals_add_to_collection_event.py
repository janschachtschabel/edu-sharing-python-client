from enum import Enum


class NotificationIntervalsAddToCollectionEvent(str, Enum):
    DAILY = "daily"
    DISABLED = "disabled"
    IMMEDIATELY = "immediately"
    WEEKLY = "weekly"

    def __str__(self) -> str:
        return str(self.value)
