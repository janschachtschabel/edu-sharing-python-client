from enum import StrEnum


class InterfaceFormat(StrEnum):
    JSON = "Json"
    TEXT = "Text"
    XML = "XML"

    def __str__(self) -> str:
        return str(self.value)
