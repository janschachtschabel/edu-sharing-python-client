from enum import StrEnum


class NotificationConfigConfigMode(StrEnum):
    INDIVIDUAL = "individual"
    UNIFORMLY = "uniformly"

    def __str__(self) -> str:
        return str(self.value)
