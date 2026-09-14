"""The OpenAI-compatible routes the gateway forwards to a provider.

``chat`` lives in ``client`` because it carries a policy -- model choice,
per-family quirks, a measured fallback. These do not: they hand a body to
``/api/v1/llm/{provider}/{route}`` and shape what comes back.

**The specification cannot say what is forwarded.** ``/v3/api-docs`` itself
covers only the gateway's own controllers. The OpenAI routes are described per
provider, in the groups ``/v3/api-docs/openai`` and
``/v3/api-docs/academiccloud`` -- but as the OpenAI surface, not as a list of
what works: the AcademicCloud's group lists ``/embeddings``, which answers 404
there (measured 2026-09-11). The list below was measured on 2026-08-28 instead,
by posting a deliberately empty body to each candidate -- every route rejects
that before doing any work, and the status code says which layer answered:

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

from ..errors import EduSharingError, ValidationError, whole_number
from ..urls import path_segment
from ._response import _boolean, _items, _number, _object, _text, _vectors
from .body import UNSET, ReasoningParam, _Vorgabe, reasoning_for_responses

if TYPE_CHECKING:  # pragma: no cover
    from .client import BildungsAPI

#: Enough room that a reasoning model does not spend the whole budget on
#: thinking. Measured 2026-08-31: 32 tokens were not enough for
#: qwen3.5-122b-a10b, 300 were.
DEFAULT_MAX_OUTPUT_TOKENS = 1000

__all__ = ["Answer", "DEFAULT_MAX_OUTPUT_TOKENS", "GeneratedImage", "Moderation",
           "call", "call_bytes", "embeddings", "images", "moderate", "respond"]


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
        # ``fullmatch``, nicht ``match``: ``$`` steht auch vor einem
        # abschliessenden ``\n``, sodass ``"embeddings\n"`` das Muster
        # bestand (Pruefung 08.09.2026).
        if not _SEGMENT.fullmatch(segment):
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

    Non-text output entries remain ignored. Invalid text values and containers
    raise ``EduSharingError`` instead of escaping as built-in exceptions.
    """
    text = []
    for i, entry in enumerate(_items(body.get("output"), "responses", "output")):
        if not isinstance(entry, dict) or isinstance(entry.get("content"), str):
            continue
        field = f"output[{i}].content"
        for j, part in enumerate(_items(entry.get("content"), "responses", field)):
            if isinstance(part, dict):
                text.append(_text(part.get("text"), "responses", f"{field}[{j}].text"))
    return "".join(text)


def _answer_from(antwort: dict[str, Any], model: str = "") -> Answer:
    """A ``responses`` body as an ``Answer``.

    Its own function because the template mode's ``/responses`` answers in the
    same shape -- one reading of ``status`` and ``incomplete_details`` for
    both, rather than two that drift apart.
    """
    details = antwort.get("incomplete_details")
    details = {} if details is None else _object(details, "responses", "incomplete_details")
    return Answer(
        text=_text_of(antwort),
        status=_text(antwort.get("status"), "responses", "status"),
        reason=_text(details.get("reason"), "responses", "incomplete_details.reason"),
        model=_text(antwort.get("model"), "responses", "model") or model,
        raw=antwort,
    )


def _images_from(answer: dict[str, Any]) -> list[GeneratedImage]:
    """An ``images/generations`` body as ``GeneratedImage`` values -- shared
    with the template mode for the same reason as ``_answer_from``."""
    images = []
    for i, item in enumerate(_items(answer.get("data"), "images/generations", "data")):
        field = f"data[{i}]"
        entry = _object(item, "images/generations", field)
        images.append(GeneratedImage(
            url=(_text(entry.get("url"), "images/generations", f"{field}.url")
                 if entry.get("url") is not None else None),
            b64=(_text(entry.get("b64_json"), "images/generations", f"{field}.b64_json")
                 if entry.get("b64_json") is not None else None),
            revised_prompt=_text(entry.get("revised_prompt"), "images/generations",
                                 f"{field}.revised_prompt")))
    return images


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
    return _answer_from(antwort, model)


async def call(
    api: BildungsAPI, route: str, body: dict[str, Any], *,
    provider: str | None = None,
) -> dict[str, Any]:
    """POST a JSON ``body`` and return the parsed JSON answer.

    The escape hatch, mirroring ``repo.raw`` on the edu-sharing side: fourteen
    routes do not need thirteen wrappers. Use it for the ones without a method
    of their own -- ``completions``, ``batches``, ``responses``. A binary
    response such as ``audio/speech`` needs ``call_bytes`` instead.

    Args:
        route: without a leading slash, e.g. ``"completions"``.
        body: the request body, passed through untouched.
        provider: overrides the client's default for this call.

    Raises:
        ValidationError: for a leading slash, and for any route that could address
            something other than it names -- ``..``, an empty segment, a query
            string. See ``_check_route``: this argument is a trust boundary,
            because it is the one a language model picks.
        EduSharingError: as the route answered.
    """
    answer = await api._request(
        "POST", _route_path(route, provider or api.provider), json=body)
    return dict(answer) if isinstance(answer, dict) else {"data": answer}


async def call_bytes(
    api: BildungsAPI, route: str, body: dict[str, Any], *,
    provider: str | None = None, max_bytes: int | None = None,
) -> bytes:
    """POST JSON and return bytes; see ``BildungsAPI.call_bytes`` for the contract."""
    if max_bytes is not None:
        whole_number("max_bytes", max_bytes, 0)
    answer = await api._request(
        "POST", _route_path(route, provider or api.provider), json=body,
        response_bytes=True, max_bytes=max_bytes)
    return bytes(answer)


def _route_path(route: str, provider: str) -> str:
    if route.startswith("/"):
        raise ValidationError(
            f"route={route!r} must be given without a leading slash -- it is "
            "appended to /api/v1/llm/{provider}/."
        )
    _check_route(route)
    return f"/api/v1/llm/{path_segment(provider)}/{route}"


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

    Raises:
        EduSharingError: on missing, duplicate or invalid indices, or vectors
            that are empty, unequal in length or contain non-finite numbers.
    """
    eingabe = [texts] if isinstance(texts, str) else list(texts)
    body = {"model": model, "input": eingabe, **extra}
    answer = await call(api, "embeddings", body, provider=provider)
    effective_input = body["input"]
    return _vectors(answer, 1 if isinstance(effective_input, str) else len(effective_input))


async def moderate(
    api: BildungsAPI, text: str, *, model: str, provider: str | None = None,
    **extra: Any,
) -> Moderation:
    """Whether a text trips the provider's content policy.

    Raises:
        EduSharingError: when the answer carries no result or an invalid
            decision, category or score. ``flagged`` must be an explicit bool;
            missing data must never be interpreted as approval.
    """
    answer = await call(api, "moderations",
                        {"model": model, "input": text, **extra},
                        provider=provider)
    results = _items(answer.get("results"), "moderations", "results")
    if not results:
        raise EduSharingError(
            "The moderation endpoint returned no result for this input. "
            "Treating that as 'not flagged' would let everything through on "
            "an outage, so it is an error here."
        )
    first = _object(results[0], "moderations", "results[0]")
    flagged = _boolean(first.get("flagged"), "moderations", "results[0].flagged")
    categories = first.get("categories")
    categories = {} if categories is None else _object(categories, "moderations", "categories")
    scores = first.get("category_scores")
    scores = {} if scores is None else _object(scores, "moderations", "category_scores")
    return Moderation(
        flagged=flagged,
        categories=tuple(name for name, hit in categories.items()
                         if _boolean(hit, "moderations", "categories entry")),
        scores={k: _number(v, "moderations", "category_scores entry") for k, v in scores.items()},
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
    return _images_from(answer)
