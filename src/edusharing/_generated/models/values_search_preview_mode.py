from enum import StrEnum


class ValuesSearchPreviewMode(StrEnum):
    RENDERINGPAGE = "RenderingPage"
    SIDEBAR = "Sidebar"

    def __str__(self) -> str:
        return str(self.value)
