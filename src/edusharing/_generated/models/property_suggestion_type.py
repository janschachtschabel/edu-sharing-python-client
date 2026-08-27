from enum import Enum


class PropertySuggestionType(str, Enum):
    AI = "AI"
    USER_PROPOSAL = "USER_PROPOSAL"

    def __str__(self) -> str:
        return str(self.value)
