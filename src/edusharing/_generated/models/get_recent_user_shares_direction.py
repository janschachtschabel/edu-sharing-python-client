from enum import StrEnum


class GetRecentUserSharesDirection(StrEnum):
    FROMUSER = "fromUser"
    REJECTEDBYUSER = "rejectedByUser"
    TOUSER = "toUser"
    TOUSERGROUPS = "toUserGroups"

    def __str__(self) -> str:
        return str(self.value)
