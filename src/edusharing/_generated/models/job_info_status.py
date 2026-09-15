from enum import Enum


class JobInfoStatus(str, Enum):
    ABORTED = "Aborted"
    FAILED = "Failed"
    FINISHED = "Finished"
    RUNNING = "Running"

    def __str__(self) -> str:
        return str(self.value)
