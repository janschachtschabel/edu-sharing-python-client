from enum import Enum


class ReportNodeMode(str, Enum):
    FEEDBACK = "Feedback"
    REPORTPROBLEM = "ReportProblem"

    def __str__(self) -> str:
        return str(self.value)
