from enum import StrEnum


class HandleParamDoiService(StrEnum):
    DISTINCT = "distinct"
    SYNC = "sync"
    UPDATE = "update"

    def __str__(self) -> str:
        return str(self.value)
