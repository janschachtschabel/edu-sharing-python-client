from enum import Enum


class ShareInfoShareType(str, Enum):
    AUTHORITY = "AUTHORITY"
    LINK = "LINK"

    def __str__(self) -> str:
        return str(self.value)
