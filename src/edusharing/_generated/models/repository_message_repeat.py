from enum import Enum


class RepositoryMessageRepeat(str, Enum):
    ALWAYS = "always"
    ONCE = "once"
    REPEAT = "repeat"

    def __str__(self) -> str:
        return str(self.value)
