from enum import Enum


class ValuesSearchPreviewMode(str, Enum):
    RENDERINGPAGE = "RenderingPage"
    SIDEBAR = "Sidebar"

    def __str__(self) -> str:
        return str(self.value)
