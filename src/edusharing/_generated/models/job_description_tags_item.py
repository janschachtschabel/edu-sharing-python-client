from enum import StrEnum


class JobDescriptionTagsItem(StrEnum):
    DELETEPERSONJOB = "DeletePersonJob"

    def __str__(self) -> str:
        return str(self.value)
