from enum import StrEnum


class GetNodesBySuggestionTypeItem(StrEnum):
    AI = "AI"
    USER_PROPOSAL = "USER_PROPOSAL"

    def __str__(self) -> str:
        return str(self.value)
