from enum import StrEnum


class UpdateNotificationStatusByReceiverIdOldStatusItem(StrEnum):
    IGNORED = "IGNORED"
    PENDING = "PENDING"
    READ = "READ"
    SENT = "SENT"

    def __str__(self) -> str:
        return str(self.value)
