from enum import StrEnum


class AdminWysiwygType(StrEnum):
    TEXTAREA = "Textarea"
    TINYMCE = "TinyMCE"

    def __str__(self) -> str:
        return str(self.value)
