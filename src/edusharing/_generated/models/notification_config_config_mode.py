from enum import Enum


class NotificationConfigConfigMode(str, Enum):
    INDIVIDUAL = "individual"
    UNIFORMLY = "uniformly"

    def __str__(self) -> str:
        return str(self.value)
