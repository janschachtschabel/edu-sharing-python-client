from enum import Enum


class FrontpageMode(str, Enum):
    COLLECTION = "collection"
    DOWNLOADS = "downloads"
    RANDOM = "random"
    RATING = "rating"
    VIEWS = "views"

    def __str__(self) -> str:
        return str(self.value)
