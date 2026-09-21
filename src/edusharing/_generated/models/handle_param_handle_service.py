from enum import StrEnum


class HandleParamHandleService(StrEnum):
    DISTINCT = "distinct"
    SYNC = "sync"
    UPDATE = "update"

    def __str__(self) -> str:
        return str(self.value)
