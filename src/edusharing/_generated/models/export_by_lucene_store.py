from enum import StrEnum


class ExportByLuceneStore(StrEnum):
    ARCHIVE = "Archive"
    WORKSPACE = "Workspace"

    def __str__(self) -> str:
        return str(self.value)
