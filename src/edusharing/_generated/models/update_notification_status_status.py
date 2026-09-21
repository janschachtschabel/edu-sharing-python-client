from enum import StrEnum


class UpdateNotificationStatusStatus(StrEnum):
    IGNORED = "IGNORED"
    PENDING = "PENDING"
    READ = "READ"
    SENT = "SENT"

    def __str__(self) -> str:
        return str(self.value)
