from enum import StrEnum


class AdminEditorType(StrEnum):
    MONACO = "Monaco"
    TEXTAREA = "Textarea"

    def __str__(self) -> str:
        return str(self.value)
