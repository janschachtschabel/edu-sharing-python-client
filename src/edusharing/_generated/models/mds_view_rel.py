from enum import StrEnum


class MdsViewRel(StrEnum):
    SUGGESTIONS = "suggestions"

    def __str__(self) -> str:
        return str(self.value)
