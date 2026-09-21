from enum import StrEnum


class SuggestionResponseDTOType(StrEnum):
    AI = "AI"
    USER_PROPOSAL = "USER_PROPOSAL"

    def __str__(self) -> str:
        return str(self.value)
