from enum import StrEnum


class SuggestionNodeStatus(StrEnum):
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    PENDING = "PENDING"

    def __str__(self) -> str:
        return str(self.value)
