from enum import Enum


class ConfigUploadPostDialog(str, Enum):
    MDS = "Mds"
    NONE = "None"
    SIMPLEEDIT = "SimpleEdit"

    def __str__(self) -> str:
        return str(self.value)
