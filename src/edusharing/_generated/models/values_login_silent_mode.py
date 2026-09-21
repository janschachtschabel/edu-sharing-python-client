from enum import StrEnum


class ValuesLoginSilentMode(StrEnum):
    IFRAME = "iframe"
    NONE = "none"
    REDIRECT = "redirect"

    def __str__(self) -> str:
        return str(self.value)
