from enum import Enum


class GetRecentUserSharesDirection(str, Enum):
    FROMUSER = "fromUser"
    REJECTEDBYUSER = "rejectedByUser"
    TOUSER = "toUser"
    TOUSERGROUPS = "toUserGroups"

    def __str__(self) -> str:
        return str(self.value)
