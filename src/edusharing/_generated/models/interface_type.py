from enum import StrEnum


class InterfaceType(StrEnum):
    GENERIC_API = "Generic_Api"
    OAI = "OAI"
    SEARCH = "Search"
    SITEMAP = "Sitemap"
    STATISTICS = "Statistics"

    def __str__(self) -> str:
        return str(self.value)
