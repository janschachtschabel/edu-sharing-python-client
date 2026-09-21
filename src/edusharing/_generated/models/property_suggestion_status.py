from enum import StrEnum


class PropertySuggestionStatus(StrEnum):
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    PENDING = "PENDING"

    def __str__(self) -> str:
        return str(self.value)
