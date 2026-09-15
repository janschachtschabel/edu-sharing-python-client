from enum import Enum


class GetStatisticsNodeGrouping(str, Enum):
    DAILY = "Daily"
    MONTHLY = "Monthly"
    NODE = "Node"
    NONE = "None"
    YEARLY = "Yearly"

    def __str__(self) -> str:
        return str(self.value)
