"""edu-sharing fuer Python.

Zugang zu einem edu-sharing-Repositorium, ohne die Metadaten-Konventionen einer
bestimmten Instanz vorauszusetzen.

    from edusharing import Repository

    with Repository("https://repository.staging.openeduhub.net") as repo:
        print(repo.about().repository_version)
        print(repo.whoami().authority)

        for treffer in repo.search("Photosynthese", fach="Biologie"):
            print(treffer.title, treffer.url)

``AsyncRepository`` ist dieselbe Oberflaeche fuer asynchronen Code.
"""

from .auth import ANONYMOUS, AnonymousCredential, BasicCredential, Credential, credential_from
from .collections import Collections
from .errors import (
    AuthenticationError,
    ConflictError,
    EduSharingError,
    NotFoundError,
    PermissionDeniedError,
    ServerError,
    TransportError,
    ValidationError,
)
from .repository import About, AsyncRepository, Identity, MetadataSet, Repository
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
    # URLs
    "normalize_repository_url",
    "rest_base",
]
