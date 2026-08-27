"""edu-sharing fuer Python.

Zugang zu einem edu-sharing-Repositorium, ohne die Metadaten-Konventionen einer
bestimmten Instanz vorauszusetzen.

    from edusharing import Repository

    with Repository("https://repository.staging.openeduhub.net") as repo:
        print(repo.about().repository_version)
        print(repo.whoami().authority)

``AsyncRepository`` ist dieselbe Oberflaeche fuer asynchronen Code.
"""

from .auth import ANONYMOUS, AnonymousCredential, BasicCredential, Credential, credential_from
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
from .repository import About, AsyncRepository, Identity, Repository
from .urls import normalize_repository_url, rest_base

__all__ = [
    # Einstieg
    "Repository",
    "AsyncRepository",
    "About",
    "Identity",
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
