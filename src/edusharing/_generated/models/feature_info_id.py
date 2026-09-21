from enum import StrEnum


class FeatureInfoId(StrEnum):
    DATAPROTECTION = "dataprotection"
    DOISERVICE = "doiService"
    HANDLESERVICE = "handleService"

    def __str__(self) -> str:
        return str(self.value)
