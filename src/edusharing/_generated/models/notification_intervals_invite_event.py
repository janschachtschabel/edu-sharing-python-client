from enum import Enum


class NotificationIntervalsInviteEvent(str, Enum):
    DAILY = "daily"
    DISABLED = "disabled"
    IMMEDIATELY = "immediately"
    WEEKLY = "weekly"

    def __str__(self) -> str:
        return str(self.value)
