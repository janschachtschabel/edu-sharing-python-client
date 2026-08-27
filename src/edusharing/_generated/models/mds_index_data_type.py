from enum import Enum


class MdsIndexDataType(str, Enum):
    DYNAMIC = "Dynamic"
    JSONDATA = "JsonData"

    def __str__(self) -> str:
        return str(self.value)
