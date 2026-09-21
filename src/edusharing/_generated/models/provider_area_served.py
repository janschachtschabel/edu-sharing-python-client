from enum import StrEnum


class ProviderAreaServed(StrEnum):
    CITY = "City"
    CONTINENT = "Continent"
    COUNTRY = "Country"
    ORGANIZATION = "Organization"
    STATE = "State"
    WORLD = "World"

    def __str__(self) -> str:
        return str(self.value)
