from enum import StrEnum


class DeleteRelationType(StrEnum):
    HASFORMAT = "hasFormat"
    ISBASEDON = "isBasedOn"
    ISDUPLICATEOF = "isDuplicateOf"
    ISPARTOF = "isPartOf"
    REFERENCES = "references"
    REPLACES = "replaces"
    REQUIRES = "requires"

    def __str__(self) -> str:
        return str(self.value)
