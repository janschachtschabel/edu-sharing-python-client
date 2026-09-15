from enum import Enum


class NodeRelationDataReverseType(str, Enum):
    HASFORMAT = "hasFormat"
    HASPART = "hasPart"
    ISBASEDON = "isBasedOn"
    ISBASISFOR = "isBasisFor"
    ISDUPLICATEOF = "isDuplicateOf"
    ISFORMATOF = "isFormatOf"
    ISPARTOF = "isPartOf"
    ISREPLACEDBY = "isReplacedBy"
    ISREQUIREDBY = "isRequiredBy"
    REFERENCES = "references"
    REPLACES = "replaces"
    REQUIRES = "requires"

    def __str__(self) -> str:
        return str(self.value)
