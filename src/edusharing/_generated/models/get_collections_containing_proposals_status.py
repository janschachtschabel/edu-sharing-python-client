from enum import StrEnum


class GetCollectionsContainingProposalsStatus(StrEnum):
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    PENDING = "PENDING"

    def __str__(self) -> str:
        return str(self.value)
