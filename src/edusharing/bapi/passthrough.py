"""The OpenAI-compatible routes the gateway forwards to a provider.

``chat`` lives in ``client`` because it carries a policy -- model choice,
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

from ..errors import EduSharingError, ValidationError
from ..urls import path_segment
from .body import UNSET, ReasoningParam, _Vorgabe, reasoning_for_responses

if TYPE_CHECKING:  # pragma: no cover
    from .client import BildungsAPI

#: Enough room that a reasoning model does not spend the whole budget on
#: thinking. Measured 2026-08-31: 32 tokens were not enough for
#: qwen3.5-122b-a10b, 300 were.
DEFAULT_MAX_OUTPUT_TOKENS = 1000

__all__ = ["Answer", "DEFAULT_MAX_OUTPUT_TOKENS", "GeneratedImage", "Moderation",
           "call", "embeddings", "images", "moderate", "respond"]


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
        ValidationError: naming the offending segment. Strict on purpose -- a route
            with a character this rejects fails loudly here rather than
            addressing something else quietly.
    """
    if not route:
        raise ValidationError("route must not be empty.")
    for segment in route.split("/"):
        if not _SEGMENT.match(segment):
            raise ValidationError(
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


@dataclass(frozen=True)
class Answer:
    """One answer from the ``responses`` route.

    Not just the text: ``status`` can be ``incomplete``, which means the budget
    ran out -- usually into thinking -- and the text stops mid-sentence.
    Measured 2026-08-31, ``qwen3.5-122b-a10b`` spent all 32 output tokens on
    its thinking process and returned that instead of an answer. Handing back
    the text alone would make that look like a finished reply.
    """

    text: str
    #: ``completed``, ``incomplete``, or whatever else the provider reports.
    status: str = ""
    #: Why it stopped, e.g. ``max_output_tokens``. Empty when it did not.
    reason: str = ""
    model: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def truncated(self) -> bool:
        """Whether the answer stops early. **Read this before using the text.**

        A provider that reports no ``status`` at all counts as not truncated:
        claiming a cut where none was reported would be inventing one. Both
        measured providers do report it.
        """
        return bool(self.status) and self.status != "completed"


def _text_of(body: dict[str, Any]) -> str:
    """The text out of the nested ``output[].content[].text``.

    Every level is checked, because every level comes from the gateway. An
    ``AttributeError`` out of here would be neither informative nor catchable
    as an ``EduSharingError``; an empty string at least says "no text".
    """
    return "".join(
        teil.get("text") or ""
        for eintrag in (body.get("output") or [])
        if isinstance(eintrag, dict)
        for teil in (eintrag.get("content") or [])
        if isinstance(teil, dict)
    )


async def respond(
    api: BildungsAPI,
    prompt: str,
    *,
    model: str,
    provider: str | None = None,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    reasoning_effort: ReasoningParam = UNSET,
    verbosity: ReasoningParam = UNSET,
    **extra: Any,
) -> Answer:
    """Ask through the ``responses`` route.

    Both providers carry it -- measured 2026-08-31, ``gpt-5.6-luna`` and
    ``gemma-4-31b-it`` both answered ``status: completed``. The parameter shape
    differs from ``chat/completions``: here it is ``reasoning={"effort": ...}``
    and ``text={"verbosity": ...}``, and the flat form is refused outright.

    Args:
        model: required. The route refuses without it, and guessing one would
            be a silent model choice. There is no virtual model here -- that
            lives on ``chat``.
        max_output_tokens: the budget. Thinking is spent from it, so a
            reasoning model needs room or comes back ``truncated``.

    Returns:
        An ``Answer``. **Check ``truncated``.**

    Raises:
        EduSharingError: without a model.
        ValidationError: for an explicit reasoning parameter this model
            cannot take, or for a route that is not addressable.
    """
    if not model:
        raise EduSharingError(
            "responses needs a model id -- the route refuses without one, and "
            "picking one here would be a silent model choice. Pass model=..., "
            "or use chat() where the library may choose."
        )
    denken = reasoning_for_responses(
        model, reasoning_effort=reasoning_effort, verbosity=verbosity)
    # ``extra`` is the escape hatch, not a second way to set the same value.
    # Spreading it last used to let it win silently, which is exactly the
    # dropped-wish this parameter pair exists to prevent. An own value is
    # honoured where the library only had a default to offer.
    for schluessel in ("reasoning", "text"):
        if schluessel not in extra:
            continue
        gesetzt = (reasoning_effort if schluessel == "reasoning" else verbosity)
        if not isinstance(gesetzt, _Vorgabe) and gesetzt is not None:
            raise ValidationError(
                f"{schluessel}={extra[schluessel]!r} in the extra arguments and "
                f"{'reasoning_effort' if schluessel == 'reasoning' else 'verbosity'}"
                f"={gesetzt!r} both set the same thing. Pass one of them."
            )
        denken.pop(schluessel, None)

    body: dict[str, Any] = {
        "model": model,
        "input": prompt,
        "max_output_tokens": max_output_tokens,
        **denken,
        **extra,
    }
    antwort = await call(api, "responses", body, provider=provider)
    return Answer(
        text=_text_of(antwort),
        status=str(antwort.get("status") or ""),
        reason=str((antwort.get("incomplete_details") or {}).get("reason") or ""),
        model=str(antwort.get("model") or model),
        raw=antwort,
    )


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
        ValidationError: for a leading slash, and for any route that could address
            something other than it names -- ``..``, an empty segment, a query
            string. See ``_check_route``: this argument is a trust boundary,
            because it is the one a language model picks.
        EduSharingError: as the route answered.
    """
    if route.startswith("/"):
        raise ValidationError(
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
