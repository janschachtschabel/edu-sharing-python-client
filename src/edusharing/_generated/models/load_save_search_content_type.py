from enum import Enum


class LoadSaveSearchContentType(str, Enum):
    ALL = "ALL"
    COLLECTIONS = "COLLECTIONS"
    COLLECTION_PROPOSALS = "COLLECTION_PROPOSALS"
    FILES = "FILES"
    FILES_AND_FOLDERS = "FILES_AND_FOLDERS"
    FOLDERS = "FOLDERS"
    TOOLPERMISSIONS = "TOOLPERMISSIONS"

    def __str__(self) -> str:
        return str(self.value)
