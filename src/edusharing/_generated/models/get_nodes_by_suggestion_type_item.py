from enum import Enum


class GetNodesBySuggestionTypeItem(str, Enum):
    AI = "AI"
    USER_PROPOSAL = "USER_PROPOSAL"

    def __str__(self) -> str:
        return str(self.value)
