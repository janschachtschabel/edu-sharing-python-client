from enum import StrEnum


class JobInfoStatus(StrEnum):
    ABORTED = "Aborted"
    FAILED = "Failed"
    FINISHED = "Finished"
    RUNNING = "Running"

    def __str__(self) -> str:
        return str(self.value)
