from enum import Enum


class EntryErrorCode(str, Enum):
    NO_PUBLISH_PERMISSION = "NO_PUBLISH_PERMISSION"
    NO_RIGHTS_ON_PERMISSIONS = "NO_RIGHTS_ON_PERMISSIONS"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"

    def __str__(self) -> str:
        return str(self.value)
