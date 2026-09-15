from enum import Enum


class SearchByLuceneStore(str, Enum):
    ARCHIVE = "Archive"
    WORKSPACE = "Workspace"

    def __str__(self) -> str:
        return str(self.value)
