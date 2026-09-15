"""The immutable value shared by vocabulary loading and snapshot persistence."""

from dataclasses import dataclass

__all__ = ["VocabularyValue"]


@dataclass(frozen=True, slots=True)
class VocabularyValue:
    """A stored value (usually a URI) and its label in the requested language."""

    uri: str
    label: str

    def __str__(self) -> str:
        return self.label
