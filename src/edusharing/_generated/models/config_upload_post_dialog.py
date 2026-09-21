from enum import StrEnum


class ConfigUploadPostDialog(StrEnum):
    MDS = "Mds"
    NONE = "None"
    SIMPLEEDIT = "SimpleEdit"

    def __str__(self) -> str:
        return str(self.value)
