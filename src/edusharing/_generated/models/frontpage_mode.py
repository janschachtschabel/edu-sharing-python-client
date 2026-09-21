from enum import StrEnum


class FrontpageMode(StrEnum):
    COLLECTION = "collection"
    DOWNLOADS = "downloads"
    RANDOM = "random"
    RATING = "rating"
    VIEWS = "views"

    def __str__(self) -> str:
        return str(self.value)
