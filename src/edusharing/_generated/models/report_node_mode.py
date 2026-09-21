from enum import StrEnum


class ReportNodeMode(StrEnum):
    FEEDBACK = "Feedback"
    REPORTPROBLEM = "ReportProblem"

    def __str__(self) -> str:
        return str(self.value)
