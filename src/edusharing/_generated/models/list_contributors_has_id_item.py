from enum import Enum


class ListContributorsHasIdItem(str, Enum):
    EMAIL = "EMAIL"
    GND = "GND"
    ORCID = "ORCID"
    ROR = "ROR"
    WIKIDATA = "WIKIDATA"

    def __str__(self) -> str:
        return str(self.value)
