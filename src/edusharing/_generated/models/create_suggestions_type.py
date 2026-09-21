from enum import StrEnum


class CreateSuggestionsType(StrEnum):
    AI = "AI"
    USER_PROPOSAL = "USER_PROPOSAL"

    def __str__(self) -> str:
        return str(self.value)
