from enum import Enum


class CollectionOptionsPublicCollections(str, Enum):
    ASSIGN = "assign"
    DELETE = "delete"
    NONE = "none"

    def __str__(self) -> str:
        return str(self.value)
