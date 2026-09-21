from enum import StrEnum


class ShareInfoShareType(StrEnum):
    AUTHORITY = "AUTHORITY"
    LINK = "LINK"

    def __str__(self) -> str:
        return str(self.value)
