"""edu-sharing fuer Python.

Zugang zu einem edu-sharing-Repositorium, ohne die Metadaten-Konventionen einer
bestimmten Instanz vorauszusetzen.

    from edusharing import Repository

    with Repository("https://repository.staging.openeduhub.net") as repo:
        print(repo.about().repository_version)
        print(repo.whoami().authority)

        for treffer in repo.search("Photosynthese", subject="Biologie"):
            print(treffer.title, treffer.url)

        node = repo.node("abc-123")
        node.update(titel="Neuer Titel")   # geprueft: wirft bei stillem Verlust

``AsyncRepository`` ist dieselbe Oberflaeche fuer asynchronen Code.
"""

from .auth import ANONYMOUS, AnonymousCredential, BasicCredential, Credential, credential_from
from .collections import Collections
from .content import NodeContent
from .errors import (
    AuthenticationError,
    ConflictError,
    EduSharingError,
    NotFoundError,
    PermissionDeniedError,
    ServerError,
    SilentDropError,
    TransportError,
    ValidationError,
)
from .info import About, Identity, MetadataSet
from .nodes import WRITE_FIELD_ALIASES, Node, Nodes
from .repository import AsyncRepository, Repository
from .results import Facet, FacetValue, SearchHit, SearchResult, UnresolvedFilter
from .search import STANDARD_FIELD_ALIASES, Search
from .urls import normalize_repository_url, rest_base
from .vocab import Vocabulary, VocabularyValue

__all__ = [
    # Einstieg
    "Repository",
    "AsyncRepository",
    "About",
    "Identity",
    "MetadataSet",
    # Suchen
    "Search",
    "Collections",
    "SearchResult",
    "SearchHit",
    "Facet",
    "FacetValue",
    "UnresolvedFilter",
    "STANDARD_FIELD_ALIASES",
    # Knoten
    "Node",
    "Nodes",
    "NodeContent",
    "WRITE_FIELD_ALIASES",
    # Vokabular
    "Vocabulary",
    "VocabularyValue",
    # Zugangsdaten
    "Credential",
    "AnonymousCredential",
    "BasicCredential",
    "ANONYMOUS",
    "credential_from",
    # Fehler
    "EduSharingError",
    "TransportError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ValidationError",
    "ConflictError",
    "ServerError",
    "SilentDropError",
    # URLs
    "normalize_repository_url",
    "rest_base",
]
