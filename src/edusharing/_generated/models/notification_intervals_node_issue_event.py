from enum import StrEnum


class NotificationIntervalsNodeIssueEvent(StrEnum):
    DAILY = "daily"
    DISABLED = "disabled"
    IMMEDIATELY = "immediately"
    WEEKLY = "weekly"

    def __str__(self) -> str:
        return str(self.value)
