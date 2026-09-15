from enum import Enum


class ProviderAreaServed(str, Enum):
    CITY = "City"
    CONTINENT = "Continent"
    COUNTRY = "Country"
    ORGANIZATION = "Organization"
    STATE = "State"
    WORLD = "World"

    def __str__(self) -> str:
        return str(self.value)
