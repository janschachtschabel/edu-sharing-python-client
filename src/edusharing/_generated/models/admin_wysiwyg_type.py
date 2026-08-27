from enum import Enum


class AdminWysiwygType(str, Enum):
    TEXTAREA = "Textarea"
    TINYMCE = "TinyMCE"

    def __str__(self) -> str:
        return str(self.value)
