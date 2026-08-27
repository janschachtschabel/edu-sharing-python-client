from enum import Enum


class PublishCopyHandleMode(str, Enum):
    DISTINCT = "distinct"
    SYNC = "sync"
    UPDATE = "update"

    def __str__(self) -> str:
        return str(self.value)
