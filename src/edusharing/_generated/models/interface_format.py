from enum import Enum


class InterfaceFormat(str, Enum):
    JSON = "Json"
    TEXT = "Text"
    XML = "XML"

    def __str__(self) -> str:
        return str(self.value)
