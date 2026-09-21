from enum import StrEnum


class ConfigRatingMode(StrEnum):
    LIKES = "likes"
    NONE = "none"
    STARS = "stars"

    def __str__(self) -> str:
        return str(self.value)
