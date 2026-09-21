from enum import StrEnum


class PublishCopyHandleMode(StrEnum):
    DISTINCT = "distinct"
    SYNC = "sync"
    UPDATE = "update"

    def __str__(self) -> str:
        return str(self.value)
