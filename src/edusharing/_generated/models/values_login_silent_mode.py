from enum import Enum


class ValuesLoginSilentMode(str, Enum):
    IFRAME = "iframe"
    NONE = "none"
    REDIRECT = "redirect"

    def __str__(self) -> str:
        return str(self.value)
