from enum import StrEnum


class HomeFolderOptionsPrivateFiles(StrEnum):
    ASSIGN = "assign"
    DELETE = "delete"
    NONE = "none"

    def __str__(self) -> str:
        return str(self.value)
