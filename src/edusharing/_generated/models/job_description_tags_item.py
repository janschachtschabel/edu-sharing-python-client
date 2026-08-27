from enum import Enum


class JobDescriptionTagsItem(str, Enum):
    DELETEPERSONJOB = "DeletePersonJob"

    def __str__(self) -> str:
        return str(self.value)
