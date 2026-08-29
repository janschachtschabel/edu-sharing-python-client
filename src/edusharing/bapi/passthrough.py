"""The OpenAI-compatible routes the gateway forwards to a provider.

``chat`` lives in ``client`` because it carries a policy -- model selection,
per-family quirks, a measured fallback. These do not: they hand a body to
``/api/v1/llm/{provider}/{route}`` and shape what comes back.

**The specification does not describe this surface.** ``/v3/api-docs`` covers
the hand-written controllers only; it knows neither ``/embeddings`` nor
``/chat/completions``, which this client has called successfully since the
start. The list below was measured on 2026-08-28 instead, by posting a
deliberately empty body to each candidate -- every route rejects that before
doing any work, and the status code says which layer answered:

===================================  ==========================================
403 (Spring Security)                the route is **not** on the gateway's list
400 / 415 / 429                      the route is on it and answered
===================================  ==========================================

Forwarded: ``chat/completions``, ``completions``, ``embeddings``,
``moderations``, ``responses``, ``images/generations``, ``images/edits``,
``audio/speech``, ``audio/transcriptions``, ``audio/translations``, ``files``,
``batches``, ``fine_tuning/jobs``, ``vector_stores``.

**Not** forwarded: ``rerank`` -- 403, the same answer an invented route gets.
``images/variations`` reaches OpenAI and gets 404 there; it is retired upstream.

**The provider decides what is possible.** Measured the same day:
``academiccloud`` lists 16 models, none of them for embedding or moderation;
``openai`` lists 132, including ``text-embedding-3-small`` and
``omni-moderation-latest``. No model is chosen for you here -- ``chat`` may do
that because there is a measured policy behind it, and there is none for these.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..errors import EduSharingError
from ..urls import path_segment

if TYPE_CHECKING:  # pragma: no cover
    from .client import BildungsAPI

__all__ = ["GeneratedImage", "Moderation", "call", "embeddings", "images",
           "moderate"]


#: What a route segment may consist of. Every forwarded route is built from
#: these -- ``chat/completions``, ``images/generations``, ``fine_tuning/jobs``.
#: A dot is deliberately absent, which is what makes ``..`` impossible.
_SEGMENT = re.compile(r"^[A-Za-z0-9_-]+$")


def _check_route(route: str) -> None:
    """Refuse a route that would address something other than it names.

    ``path_segment`` cannot do this job: it percent-encodes ``/``, and a route
    needs that separator. So the rule is a check rather than an escape.

    Measured on 2026-08-28, before this existed::

        call("../../administration/account")
        -> https://.../api/v1/administration/account

    The request left ``/api/v1/llm/{provider}/``, reached the administration
    API and took the ``X-API-KEY`` with it. A query string smuggled in the same
    way (``embeddings?admin=1``) survived too.

    This is the boundary ``path_segment``'s own docstring describes: an
    identifier that is "not typed by a developer but arrives from a language
    model". ``call`` is precisely the method whose argument a model chooses.

    Raises:
        ValueError: naming the offending segment. Strict on purpose -- a route
            with a character this rejects fails loudly here rather than
            addressing something else quietly.
    """
    if not route:
        raise ValueError("route must not be empty.")
    for segment in route.split("/"):
        if not _SEGMENT.match(segment):
            raise ValueError(
                f"route={route!r} is not addressable: the segment "
                f"{segment!r} is empty or carries something other than "
                "letters, digits, '_' and '-'. Routes look like "
                "'embeddings' or 'images/generations'."
            )


@dataclass(frozen=True)
class Moderation:
    """What a moderation call decided.

    The raw answer carries a dozen-odd category booleans next to a score for
    each. A caller decides one thing -- let it through or not -- and then wants
    to know what tripped it.
    """

    flagged: bool
    #: The categories that came back true, in the order the answer listed them.
    categories: tuple[str, ...]
    #: Every category's score, flagged or not. Useful for a threshold of one's
    #: own: ``flagged`` is the provider's judgement, not necessarily yours.
    scores: dict[str, float] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GeneratedImage:
    """One generated image -- as a link or as bytes, never as both.

    Which one arrives depends on ``response_format``. Merging them into a
    single field would leave the caller guessing what it holds.
    """

    url: str | None = None
    #: base64, exactly as delivered. Decoding it here would hand back bytes
    #: nobody asked for and hide the encoding from the caller.
    b64: str | None = None
    #: Some models rewrite the prompt before drawing and say so.
    revised_prompt: str = ""


async def call(
    api: BildungsAPI, route: str, body: dict[str, Any], *,
    provider: str | None = None,
) -> dict[str, Any]:
    """POST ``body`` to one forwarded route and return the parsed answer.

    The escape hatch, mirroring ``repo.raw`` on the edu-sharing side: fourteen
    routes do not need thirteen wrappers. Use it for the ones without a method
    of their own -- ``audio/speech``, ``batches``, ``responses``.

    Args:
        route: without a leading slash, e.g. ``"audio/speech"``.
        body: the request body, passed through untouched.
        provider: overrides the client's default for this call.

    Raises:
        ValueError: for a leading slash, and for any route that could address
            something other than it names -- ``..``, an empty segment, a query
            string. See ``_check_route``: this argument is a trust boundary,
            because it is the one a language model picks.
        EduSharingError: as the route answered.
    """
    if route.startswith("/"):
        raise ValueError(
            f"route={route!r} must be given without a leading slash -- it is "
            "appended to /api/v1/llm/{provider}/."
        )
    _check_route(route)
    which = provider or api.provider
    # Reaching into the client's request plumbing: retry, concurrency limit and
    # the X-API-KEY header live there, and duplicating them here would be two
    # things to keep in step.
    answer = await api._request(
        "POST", f"/api/v1/llm/{path_segment(which)}/{route}", json=body,
    )
    return dict(answer) if isinstance(answer, dict) else {"data": answer}


async def embeddings(
    api: BildungsAPI, texts: str | list[str], *, model: str,
    provider: str | None = None, **extra: Any,
) -> list[list[float]]:
    """Vectors for one or more texts.

    Args:
        texts: a string or a list of them. A single string still yields a list
            of one vector -- the same shape either way, because a return type
            that changes with the input forces every caller to check it.
        model: required. ``academiccloud`` has no embedding model, so guessing
            one would fail in a way that looks like a library bug.

    Returns:
        One vector per input, in the order the input had. The answer carries an
        ``index`` per entry and is sorted by it here: the API may reorder, and
        a vector matched to the wrong text is silent nonsense.
    """
    eingabe = [texts] if isinstance(texts, str) else list(texts)
    answer = await call(api, "embeddings",
                        {"model": model, "input": eingabe, **extra},
                        provider=provider)
    entries = answer.get("data") or []
    ordered = sorted(entries, key=lambda e: e.get("index", 0))
    return [list(e.get("embedding") or []) for e in ordered]


async def moderate(
    api: BildungsAPI, text: str, *, model: str, provider: str | None = None,
    **extra: Any,
) -> Moderation:
    """Whether a text trips the provider's content policy.

    Raises:
        EduSharingError: when the answer carries no result. Reading an empty
            list as "not flagged" would make an outage look like approval --
            the one reading that lets everything through.
    """
    answer = await call(api, "moderations",
                        {"model": model, "input": text, **extra},
                        provider=provider)
    results = answer.get("results") or []
    if not results:
        raise EduSharingError(
            "The moderation endpoint returned no result for this input. "
            "Treating that as 'not flagged' would let everything through on "
            "an outage, so it is an error here."
        )
    first = results[0]
    categories = first.get("categories") or {}
    return Moderation(
        flagged=bool(first.get("flagged")),
        categories=tuple(name for name, hit in categories.items() if hit),
        scores={k: float(v) for k, v in
                (first.get("category_scores") or {}).items()},
        raw=answer,
    )


async def images(
    api: BildungsAPI, prompt: str, *, model: str, provider: str | None = None,
    **extra: Any,
) -> list[GeneratedImage]:
    """Generate images from a prompt.

    ``extra`` is passed through -- ``n``, ``size``, ``quality``,
    ``response_format`` are the provider's business, not this library's.
    """
    answer = await call(api, "images/generations",
                        {"model": model, "prompt": prompt, **extra},
                        provider=provider)
    return [
        GeneratedImage(
            url=entry.get("url"),
            b64=entry.get("b64_json"),
            revised_prompt=entry.get("revised_prompt") or "",
        )
        for entry in (answer.get("data") or [])
    ]
