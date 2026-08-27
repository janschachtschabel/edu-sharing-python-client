from enum import Enum


class FeatureInfoId(str, Enum):
    DATAPROTECTION = "dataprotection"
    DOISERVICE = "doiService"
    HANDLESERVICE = "handleService"

    def __str__(self) -> str:
        return str(self.value)
