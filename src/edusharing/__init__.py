"""edu-sharing for Python.

Access to an edu-sharing repository without presupposing the metadata
conventions of any particular instance.

    from edusharing import Repository

    with Repository("https://repository.staging.openeduhub.net") as repo:
        print(repo.about().repository_version)
        print(repo.whoami().authority)

        for hit in repo.search("Photosynthese", subject="Biologie"):
            print(hit.title, hit.url)

        node = repo.node("abc-123")
        node.update(title="New title")     # verified: raises on a silent drop

``AsyncRepository`` is the same surface for asynchronous code.
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
    # Entry point
    "Repository",
    "AsyncRepository",
    "About",
    "Identity",
    "MetadataSet",
    # Searching
    "Search",
    "Collections",
    "SearchResult",
    "SearchHit",
    "Facet",
    "FacetValue",
    "UnresolvedFilter",
    "STANDARD_FIELD_ALIASES",
    # Nodes
    "Node",
    "Nodes",
    "NodeContent",
    "WRITE_FIELD_ALIASES",
    # Vocabulary
    "Vocabulary",
    "VocabularyValue",
    # Credentials
    "Credential",
    "AnonymousCredential",
    "BasicCredential",
    "ANONYMOUS",
    "credential_from",
    # Errors
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
