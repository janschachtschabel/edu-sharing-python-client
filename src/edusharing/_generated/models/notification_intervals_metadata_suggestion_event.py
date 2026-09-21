from enum import StrEnum


class NotificationIntervalsMetadataSuggestionEvent(StrEnum):
    DAILY = "daily"
    DISABLED = "disabled"
    IMMEDIATELY = "immediately"
    WEEKLY = "weekly"

    def __str__(self) -> str:
        return str(self.value)
