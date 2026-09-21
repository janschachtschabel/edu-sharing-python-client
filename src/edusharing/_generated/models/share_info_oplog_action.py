from enum import StrEnum


class ShareInfoOplogAction(StrEnum):
    CREATE = "CREATE"
    DELETE = "DELETE"
    UPDATE = "UPDATE"

    def __str__(self) -> str:
        return str(self.value)
