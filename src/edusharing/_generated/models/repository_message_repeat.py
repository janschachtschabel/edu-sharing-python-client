from enum import StrEnum


class RepositoryMessageRepeat(StrEnum):
    ALWAYS = "always"
    ONCE = "once"
    REPEAT = "repeat"

    def __str__(self) -> str:
        return str(self.value)
