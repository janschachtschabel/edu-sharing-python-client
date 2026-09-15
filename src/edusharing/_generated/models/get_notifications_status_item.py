from enum import Enum


class GetNotificationsStatusItem(str, Enum):
    IGNORED = "IGNORED"
    PENDING = "PENDING"
    READ = "READ"
    SENT = "SENT"

    def __str__(self) -> str:
        return str(self.value)
