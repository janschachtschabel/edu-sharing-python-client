from enum import Enum


class AdminEditorType(str, Enum):
    MONACO = "Monaco"
    TEXTAREA = "Textarea"

    def __str__(self) -> str:
        return str(self.value)
