from enum import Enum


class ContextMenuEntryScopesItem(str, Enum):
    COLLECTIONSCOLLECTION = "CollectionsCollection"
    COLLECTIONSREFERENCES = "CollectionsReferences"
    CREATEMENU = "CreateMenu"
    OER = "Oer"
    RENDER = "Render"
    SEARCH = "Search"
    WORKSPACELIST = "WorkspaceList"
    WORKSPACETREE = "WorkspaceTree"

    def __str__(self) -> str:
        return str(self.value)
