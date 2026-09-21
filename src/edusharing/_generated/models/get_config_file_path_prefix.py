from enum import StrEnum


class GetConfigFilePathPrefix(StrEnum):
    CLUSTER = "cluster"
    CLUSTERAPPLICATIONS = "cluster/applications"
    DEFAULTS = "defaults"
    DEFAULTSDATABASE = "defaults/database"
    DEFAULTSMAILTEMPLATES = "defaults/mailtemplates"
    DEFAULTSMETADATASETS = "defaults/metadatasets"
    NODE = "node"

    def __str__(self) -> str:
        return str(self.value)
