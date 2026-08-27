from enum import Enum


class ExportByLuceneStore(str, Enum):
    ARCHIVE = "Archive"
    WORKSPACE = "Workspace"

    def __str__(self) -> str:
        return str(self.value)
