from enum import Enum


class MdsViewRel(str, Enum):
    SUGGESTIONS = "suggestions"

    def __str__(self) -> str:
        return str(self.value)
