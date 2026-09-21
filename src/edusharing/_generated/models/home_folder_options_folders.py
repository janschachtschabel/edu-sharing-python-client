from enum import StrEnum


class HomeFolderOptionsFolders(StrEnum):
    ASSIGN = "assign"
    DELETE = "delete"
    NONE = "none"

    def __str__(self) -> str:
        return str(self.value)
