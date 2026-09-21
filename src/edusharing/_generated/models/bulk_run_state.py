from enum import StrEnum


class BulkRunState(StrEnum):
    NEW = "New"
    PUBLISHED = "Published"

    def __str__(self) -> str:
        return str(self.value)
