from enum import Enum


class ConfigRatingMode(str, Enum):
    LIKES = "likes"
    NONE = "none"
    STARS = "stars"

    def __str__(self) -> str:
        return str(self.value)
