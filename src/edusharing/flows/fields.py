"""Turning short-name values into edu-sharing properties.

Its own module because ``add_material`` and ``update_material`` both need it and
neither owns it -- and because "translate a caller's words into the repository's
words" is a different job from "create material".
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from .find import field_property

if TYPE_CHECKING:  # pragma: no cover
    from ..repository import AsyncRepository

__all__ = ["name_from_title", "resolve_vocabulary"]


#: ``cm:name`` is the key inside the parent folder, not a display title. These
#: characters make edu-sharing reject it or mangle it.
_UNSAFE_IN_NAME = re.compile(r"[^\w.\- ]+", re.UNICODE)


def name_from_title(title: str) -> str:
    """Derive a usable ``cm:name`` from a title.

    Callers think in titles; the repository needs a key. Deriving it here saves
    the caller a decision they have no basis to make -- and ``rename_if_exists``
    on the node layer handles the collision this may cause.
    """
    name = _UNSAFE_IN_NAME.sub("", title).strip()
    return (name or "material")[:80]


async def resolve_vocabulary(
    repo: AsyncRepository, aliases: dict[str, Any]
) -> tuple[dict[str, list[str]], list[dict[str, Any]]]:
    """Turn ``{"subject": "Biologie"}`` into ``{"ccm:taxonid": ["<uri>"]}``.

    Returns the resolved properties and everything that could not be resolved.
    Unresolvable values are NOT sent: a value the metadata set does not know is
    rejected by the repository or stored as an unusable string, and both are
    worse than a reported gap.

    **One label, one value -- deliberately, and unlike the search.** Measured
    2026-08-31, 25 subject labels sit in two vocabularies at once, once under
    ``discipline`` and once under ``hochschulfaechersystematik``. Searching
    filters on both (``Vocabulary.resolve_all``), because finding half the
    material while looking like all of it is a wrong answer. Writing takes the
    first, because writing both would *assert* both: tagging a year 6 worksheet
    as a university subject is a claim, not a widening. A caller who wants the
    other one passes its URI, which goes through untouched.
    """
    resolved: dict[str, list[str]] = {}
    unresolved: list[dict[str, Any]] = []

    for short_name, value in aliases.items():
        prop = field_property(repo, short_name)
        values = value if isinstance(value, list) else [value]
        uris: list[str] = []
        for single in values:
            text = str(single)
            # A URI is already what the repository wants -- passing it through
            # the resolver would only fail on it.
            if text.startswith(("http://", "https://")):
                uris.append(text)
                continue
            uri = await repo.vocab.resolve(prop, text)
            if uri is None:
                suggestions = [v.label for v in await repo.vocab.suggest(prop, text)][:5]
                unresolved.append(
                    {"field": short_name, "value": text, "suggestions": suggestions}
                )
                continue
            uris.append(uri)
        if uris:
            resolved[prop] = uris

    return resolved, unresolved
