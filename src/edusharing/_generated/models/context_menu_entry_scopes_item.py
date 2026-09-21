from enum import StrEnum


class ContextMenuEntryScopesItem(StrEnum):
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
