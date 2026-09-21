from enum import StrEnum


class SearchByPropertyCombineMode(StrEnum):
    AND = "AND"
    OR = "OR"

    def __str__(self) -> str:
        return str(self.value)
