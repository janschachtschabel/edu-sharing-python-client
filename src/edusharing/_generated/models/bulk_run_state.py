from enum import Enum


class BulkRunState(str, Enum):
    NEW = "New"
    PUBLISHED = "Published"

    def __str__(self) -> str:
        return str(self.value)
