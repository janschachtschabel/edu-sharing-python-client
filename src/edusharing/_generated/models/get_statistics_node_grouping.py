from enum import StrEnum


class GetStatisticsNodeGrouping(StrEnum):
    DAILY = "Daily"
    MONTHLY = "Monthly"
    NODE = "Node"
    NONE = "None"
    YEARLY = "Yearly"

    def __str__(self) -> str:
        return str(self.value)
