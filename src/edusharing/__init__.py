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

**Where a name comes from.** Almost everything is here, at the top:

===============================  ========================================
``from edusharing import ...``   the repository, its results, its errors
``edusharing.agent``             building blocks for AI use
``edusharing.bapi``              the LLM gateway -- a separate service
``edusharing.extraction``        the text-extraction service -- likewise
``edusharing.metadata_agent``    the metadata agent -- likewise
===============================  ========================================

The flows need no import of their own: they hang off a connection as
``repo.flows.search(...)``. The three neighbouring services get a module of
their own because they have an address of their own, and a connection to a
repository says nothing about whether they exist.
"""

from importlib.metadata import PackageNotFoundError as _PackageNotFound
from importlib.metadata import version as _metadata_version

from .auth import ANONYMOUS, AnonymousCredential, BasicCredential, Credential
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
from .flows.language import GERMAN, LanguageProfile
from .info import About, Identity, MetadataSet
from .nodes import WRITE_FIELD_ALIASES, Node
from .repository import AsyncRepository, Repository
from .results import Facet, FacetValue, SearchHit, SearchResult, UnresolvedFilter
from .search import STANDARD_FIELD_ALIASES
from .vocab import Vocabulary, VocabularyValue

#: The installed version. Read from the package metadata rather than written
#: here: two copies of the same number drift, and the wrong one only surfaces
#: when somebody quotes it in a bug report. ``"0+unknown"`` when the package is
#: not installed at all -- running straight from a source tree.
try:
    __version__ = _metadata_version("edu-sharing-python-client")
except _PackageNotFound:  # pragma: no cover - only without an install
    __version__ = "0+unknown"

__all__ = [
    "__version__",
    # Entry point
    "Repository",
    "AsyncRepository",
    "About",
    "Identity",
    "MetadataSet",
    # Searching
    "SearchResult",
    "SearchHit",
    "Facet",
    "FacetValue",
    "UnresolvedFilter",
    "STANDARD_FIELD_ALIASES",
    # Nodes
    "Node",
    "NodeContent",
    "WRITE_FIELD_ALIASES",
    # Vocabulary
    "Vocabulary",
    "VocabularyValue",
    # Flows -- reached as repo.flows.*, but reranking takes a word list
    "LanguageProfile",
    "GERMAN",
    # Credentials
    "Credential",
    "AnonymousCredential",
    "BasicCredential",
    "ANONYMOUS",
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
]
