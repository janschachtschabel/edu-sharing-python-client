from enum import StrEnum


class MdsIndexDataType(StrEnum):
    DYNAMIC = "Dynamic"
    JSONDATA = "JsonData"

    def __str__(self) -> str:
        return str(self.value)
