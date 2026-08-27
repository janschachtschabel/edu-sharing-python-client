from enum import Enum


class DeleteRelationType(str, Enum):
    HASFORMAT = "hasFormat"
    ISBASEDON = "isBasedOn"
    ISDUPLICATEOF = "isDuplicateOf"
    ISPARTOF = "isPartOf"
    REFERENCES = "references"
    REPLACES = "replaces"
    REQUIRES = "requires"

    def __str__(self) -> str:
        return str(self.value)
