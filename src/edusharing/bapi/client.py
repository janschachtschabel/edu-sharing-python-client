"""Access to the b-api, the LLM gateway of OpenEduHub.

Measured against staging:

* **Auth via ``X-API-KEY``**, not Bearer -- the mirror image of edu-sharing,
  where Basic applies and a Bearer is ignored.
* **Two providers**: ``academiccloud`` (with the ``demand`` load figure) and
  ``openai`` (without). A third name ends in ``400 Provider ... not found``.
* **No quota headers and no ``retry-after``.** A client cannot see its
  remaining allowance and notices a limit only when it fails; exponential
  backoff is all that is possible.
* **The OpenAPI document is at ``/v3/api-docs``, and it is incomplete.**
  ``/openapi.json``, ``/docs`` and ``/health`` serve the Angular frontend;
  ``/v3/api-docs`` answers with 68 kB of Springdoc output. It describes the
  hand-written controllers only and knows neither ``/api/v1/llm/{provider}/models``
  nor ``/chat/completions`` -- the two routes this client has always used.
  Measured 2026-08-28; see ``passthrough`` for how the real list was found.

A separate HTTP path rather than the edu-sharing ``Transport``: that one's
credential boundary and error mapping are cut for a repository (basic auth,
``DAO*`` exceptions). Parameterising it for both would have made each side less
clear. The retry logic is similar; should a third consumer appear, extracting
it would be worth it.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, date, datetime
from typing import Any, Self

import httpx

from ..errors import (
    EduSharingError,
    ValidationError,
    at_least,
    error_from_response,
)
from ..urls import path_segment, refuse_userinfo
from . import passthrough
from .body import UNSET, ReasoningParam, build_body, read_answer
from .models import (
    LoadReport,
    Model,
    is_rankable,
    load_report,
    pick_model,
    rank_among,
    rank_models,
)

__all__ = ["BildungsAPI"]

#: See ``edusharing.transport.logger``. Under automatic model selection this is
#: the only place that says which candidates were tried and why they failed.
logger = logging.getLogger(__name__)

ENV_KEY = "B_API_KEY"
ENV_BASE_URL = "B_API_BASE_URL"

# There is deliberately no default address. Until 2026-08-28 the staging
# gateway stood here, so setting only B_API_KEY sent the key to a host nobody
# had chosen; ``extraction`` has always refused exactly that.
#
# The provider does have one. It decides which models exist -- measured
# 2026-08-28, ``academiccloud`` lists 16, none for embedding or moderation,
# while ``openai`` lists 132 including both.
DEFAULT_PROVIDER = "academiccloud"

#: Measured 2026-08-21: up to 26 concurrent requests without error, occasional
#: 502 from 19 onwards. The limit is NOT stable -- on 08-12 it was 2. Re-measure
#: before any capacity planning.
DEFAULT_MAX_CONCURRENCY = 6

#: Individual requests sat in the queue for up to 94 s.
DEFAULT_TIMEOUT = 180.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_BASE = 2.5

#: ``demand`` fluctuates by the minute -- a long cache would decide the model
#: choice on stale numbers. No cache at all costs an extra request per call.
DEFAULT_MODELS_CACHE_SECONDS = 30.0

#: ``models_cache_seconds=CACHE_FOREVER`` asks once and never again. Right for
#: a script that runs for a minute; **wrong for a long-lived service**, which
#: would then choose models on figures from hours ago. ``0`` disables the cache
#: and costs one extra request per call.
CACHE_FOREVER = float("inf")

#: How often one candidate is retried before the next model is tried instead.
#: A 503 is retryable, so without this the transport spent the full
#: ``max_retries`` on a busy model -- roughly 17 s at the default backoff --
#: while another model stood right next to it. The **last** candidate keeps the
#: full budget: there is nothing left to switch to, so waiting is all there is.
#:
#: A 429 is the exception that this cannot help: measured, the AcademicCloud
#: answers "API rate limit exceeded" for the key, not for the model, so the
#: next candidate fails just as fast. The run then ends at the last candidate,
#: which waits as before.
DEFAULT_RETRIES_BEFORE_SWITCHING = 1

#: Status codes where a second attempt can succeed. 404 is deliberately absent:
#: "This is not a chat model" will not improve on the fourth try.
RETRYABLE = frozenset({429, 500, 502, 503, 504})

#: How many models are tried in turn under automatic selection. Measured: a
#: model can report ``status: ready`` and still not answer (``503 Model pricing
#: unavailable``). With an explicit model id there is **no** fallback -- that
#: would be a silent substitution.
DEFAULT_MODEL_ATTEMPTS = 3


class BildungsAPI:
    """Client for the b-api.

    Args:
        api_key: the key. Required.
        base_url: gateway address.
        provider: ``academiccloud`` or ``openai``.
        max_concurrency: concurrent requests.
        models_cache_seconds: how long the model list stays valid. ``0``
            disables the cache, ``CACHE_FOREVER`` asks exactly once.
        retries_before_switching: how often one model is retried before the
            next candidate is tried instead. The last candidate keeps the full
            ``max_retries`` -- there is nothing left to switch to.
        virtual_models: names for groups of models, e.g.
            ``{"schnell": ["qwen3.6-35b-a3b", "gemma-4-31b-it"]}``.
            ``chat(model="schnell")`` then takes the least loaded of them.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str,
        provider: str = DEFAULT_PROVIDER,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
        backoff_base: float = DEFAULT_BACKOFF_BASE,
        models_cache_seconds: float = DEFAULT_MODELS_CACHE_SECONDS,
        retries_before_switching: int = DEFAULT_RETRIES_BEFORE_SWITCHING,
        virtual_models: Mapping[str, Sequence[str]] | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if not api_key:
            raise EduSharingError(
                f"The b-api needs a key. Either set {ENV_KEY} or pass "
                "BildungsAPI(api_key=...)."
            )
        at_least("timeout", timeout, 0.001)
        at_least("max_retries", max_retries, 0)
        at_least("max_concurrency", max_concurrency, 1)
        at_least("backoff_base", backoff_base, 0)
        at_least("models_cache_seconds", models_cache_seconds, 0)
        at_least("retries_before_switching", retries_before_switching, 0)
        self._api_key = api_key
        refuse_userinfo(
            base_url,
            instead=f"The b-api takes a key -- BildungsAPI(api_key=...) or {ENV_KEY} "
            "-- not a user.",
        )
        self.base_url = base_url.rstrip("/")
        self.provider = provider
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.models_cache_seconds = models_cache_seconds
        self.retries_before_switching = retries_before_switching
        #: Names the caller gave to groups of models. ``chat(model="schnell")``
        #: then takes the least loaded of the group. Empty by default: the
        #: library invents no names, because a name only helps if the caller
        #: knows what is behind it.
        self.virtual_models: dict[str, list[str]] = {
            name: list(ids) for name, ids in (virtual_models or {}).items()
        }
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._client = client or httpx.AsyncClient(timeout=timeout)
        self._owns_client = client is None
        self._models_cache: tuple[float, list[Model]] | None = None
        self._models_lock = asyncio.Lock()
        #: The model the last answer came from. Under automatic selection this
        #: is the only place that says whose answer you are reading.
        self.last_model: str | None = None

    @classmethod
    def from_env(cls, **kwargs: Any) -> BildungsAPI:
        """Build a client from ``B_API_KEY`` and ``B_API_BASE_URL``.

        Raises:
            EduSharingError: when either is unset. There is no default
                address on purpose -- see the note at ``ENV_BASE_URL``.
        """
        key = os.environ.get(ENV_KEY, "")
        if not key:
            raise EduSharingError(
                f"{ENV_KEY} is not set. Either set the variable or pass the key: "
                "BildungsAPI(api_key=...)."
            )
        adresse = os.environ.get(ENV_BASE_URL, "").strip()
        if not adresse and "base_url" not in kwargs:
            raise EduSharingError(
                f"{ENV_BASE_URL} is not set. Point it at the gateway you"
                " actually use -- there is no default, because a wrong one"
                " sends your API key to a host you did not choose."
            )
        if adresse:
            kwargs.setdefault("base_url", adresse)
        return cls(key, **kwargs)

    # --- Lifecycle --------------------------------------------------------

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()

    # --- Requests ---------------------------------------------------------

    async def models(self, provider: str | None = None) -> list[Model]:
        """The models of this provider, with load figures where reported."""
        which = provider or self.provider

        def aus_dem_cache() -> list[Model] | None:
            if (
                self.models_cache_seconds > 0
                and self._models_cache
                and which == self.provider
                and time.monotonic() - self._models_cache[0]
                < self.models_cache_seconds
            ):
                return self._models_cache[1]
            return None

        gemerkt = aus_dem_cache()
        if gemerkt is not None:
            return gemerkt

        async with self._models_lock:
            # Again, inside the lock. Without this the lock only queues the
            # callers up: each one still fetches, so a cold start with six
            # concurrent calls made six requests -- against a gateway that
            # answers 429 for the key, not the model.
            gemerkt = aus_dem_cache()
            if gemerkt is not None:
                return gemerkt

            now = time.monotonic()
            response = await self._request("GET", f"/api/v1/llm/{path_segment(which)}/models")
            raw = response.get("data") if isinstance(response, dict) else response
            models = [Model.from_response(m) for m in (raw or [])]
            if which == self.provider:
                self._models_cache = (now, models)
            return models

    async def load(
        self, provider: str | None = None, *, on: date | None = None,
    ) -> LoadReport:
        """What the provider says about its models right now.

        Ask this once at start-up and log ``summary()``: whoever reads the log
        later then knows what the model choice was made on. It uses the same
        cached list as everything else, so it costs nothing extra when the
        cache is warm.

        Args:
            on: the day to judge ``shutdown_date`` against. Defaults to today
                in UTC.

        Returns:
            A ``LoadReport``. **Read ``reports_load`` first** -- at OpenAI it
            is false and the ranking says nothing about queues.
        """
        which = provider or self.provider
        # UTC, not the local day: the retirement dates come from the provider,
        # and a local date boundary would shift them by up to a day.
        return load_report(await self.models(which), which,
                           on or datetime.now(UTC).date())

    async def _resolve_group(
        self, model: str | Sequence[str] | None, which: str
    ) -> list[str] | None:
        """The model ids behind ``model``, or ``None`` if it names just one.

        Raises:
            EduSharingError: when a group name is also a real model id. Which
                of the two was meant would then depend on lookup order, and the
                answer would come from a model nobody chose.
        """
        if model is None or (isinstance(model, str) and not model):
            return None
        if not isinstance(model, str):
            return list(model)
        if model not in self.virtual_models:
            return None

        vorhanden = {m.id for m in await self.models(which)}
        if model in vorhanden:
            raise EduSharingError(
                f"{model!r} is both a group in virtual_models and a model "
                f"offered by {which!r}. Rename the group -- otherwise which of "
                "the two answers depends on lookup order."
            )
        return self.virtual_models[model]

    async def chat(
        self,
        prompt: str | list[dict[str, str]],
        *,
        model: str | Sequence[str] | None = None,
        provider: str | None = None,
        max_tokens: int = 1000,
        temperature: float = 0.0,
        thinking: bool = False,
        system: str | None = None,
        reasoning_effort: ReasoningParam = UNSET,
        verbosity: ReasoningParam = UNSET,
    ) -> str:
        """Send a request and return the answer text.

        Args:
            prompt: a string or a ready message list.
            model: three ways to say it.

                * a model id -- exactly this model, no substitution;
                * a list of ids, or the name of a group from
                  ``virtual_models`` -- the least loaded of them, and the next
                  one if it does not answer;
                * nothing -- the least loaded ready text model of the provider.

                Only the AcademicCloud reports load. At OpenAI a group keeps
                the order you wrote it in, which makes it a fallback chain.
            system: system message; effective only when ``prompt`` is a string.
            thinking: allow Qwen3 to think. Defaults to ``False`` -- see
                ``body``.

        Returns:
            The answer text. If the budget went into thinking, the text comes
            from ``reasoning`` rather than ``content``.

        Raises:
            EduSharingError: when a group name is also a real model id, when a
                named model is not offered, or when none of the candidates
                answered.
        """
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
            if system:
                messages.insert(0, {"role": "system", "content": system})
        else:
            messages = prompt

        which = provider or self.provider
        path = f"/api/v1/llm/{path_segment(which)}/chat/completions"

        def body_for(mid: str) -> dict[str, Any]:
            return build_body(
                mid, messages,
                max_tokens=max_tokens, temperature=temperature, thinking=thinking,
                reasoning_effort=reasoning_effort, verbosity=verbosity,
            )

        gruppe = await self._resolve_group(model, which)

        if gruppe is not None:
            candidates = rank_among(await self.models(which), gruppe)
        elif isinstance(model, str) and model:
            self.last_model = model
            return read_answer(await self._request("POST", path, json=body_for(model)))
        else:
            angebot = await self.models(which)
            if not is_rankable(angebot):
                # Nothing to choose on. Ranking would be alphabetical order in
                # a ranking's clothes -- measured, that picked babbage-002 out
                # of OpenAI's 132 and failed three times before saying so.
                raise ValidationError(
                    f"Provider {which!r} reports neither load nor output types "
                    f"for any of its {len(angebot)} models, so there is nothing "
                    "to choose on. Pass model=\"...\" for one, or model=[...] "
                    "for a group; ask load() to see what is offered."
                )
            candidates = rank_models(angebot)
            if not candidates:
                raise EduSharingError(f"No ready text model at provider {which!r}.")

        # A group is an explicit list: whoever names five means five. The cap
        # belongs to the automatic choice, where the library is guessing.
        versuche = candidates if gruppe is not None \
            else candidates[:DEFAULT_MODEL_ATTEMPTS]

        return read_answer(await self._first_that_answers(versuche, path, body_for))

    async def _first_that_answers(
        self,
        versuche: list[Model],
        path: str,
        body_for: Callable[[str], dict[str, Any]],
    ) -> dict[str, Any]:
        """Try the candidates in order and return the first answer.

        Switching beats waiting while another candidate remains: a 503 is
        retryable, so without a cap the transport spent the full
        ``max_retries`` on a busy model with a second one standing next to it.
        The last candidate keeps the full budget -- there is nothing left to
        switch to.

        Raises:
            EduSharingError: when none of them answered, naming each failure.
        """
        failures: list[str] = []
        for nummer, candidate in enumerate(versuche):
            letzter = nummer == len(versuche) - 1
            # Nur senken, nie anheben: wer max_retries=0 setzt, will genau
            # einen Versuch je Modell -- auch beim ersten Kandidaten.
            budget = None if letzter else min(self.retries_before_switching,
                                              self.max_retries)
            try:
                response = await self._request(
                    "POST", path, json=body_for(candidate.id), max_retries=budget)
            except EduSharingError as exc:
                # A "ready" model may still not answer. Whoever left the choice
                # to the library wants an answer -- not the news that the first
                # candidate happens to be unbillable right now.
                failures.append(f"{candidate.id}: {exc}")
                logger.info(
                    "model %s did not answer (%s), trying the next candidate",
                    candidate.id, type(exc).__name__,
                )
                continue
            if candidate.is_retired_on(datetime.now(UTC).date()):
                # Not excluded: it still answers, and 19 of OpenAI's 132 were
                # already past their date on 2026-08-31. But when the LIBRARY
                # chose it, nobody else is in a position to notice.
                logger.warning(
                    "chose %s, which the provider retired on %s",
                    candidate.id, candidate.shutdown_date,
                )
            self.last_model = candidate.id
            return dict(response)

        raise EduSharingError(
            "None of the models tried answered. " + " | ".join(failures)
        )

    # --- The forwarded OpenAI routes --------------------------------------
    #
    # Thin on purpose: these carry no model policy, so they belong beside
    # rather than inside it. The measurements behind them are in
    # ``passthrough``.

    async def embeddings(
        self, texts: str | list[str], *, model: str,
        provider: str | None = None, **extra: Any,
    ) -> list[list[float]]:
        """Vectors for one or more texts. See ``passthrough.embeddings``."""
        return await passthrough.embeddings(
            self, texts, model=model, provider=provider, **extra)

    async def moderate(
        self, text: str, *, model: str, provider: str | None = None,
        **extra: Any,
    ) -> passthrough.Moderation:
        """Whether a text trips the content policy. See ``passthrough.moderate``.

        **An empty answer raises** rather than reading as "not flagged" -- that
        reading would let everything through during an outage.
        """
        return await passthrough.moderate(
            self, text, model=model, provider=provider, **extra)

    async def images(
        self, prompt: str, *, model: str, provider: str | None = None,
        **extra: Any,
    ) -> list[passthrough.GeneratedImage]:
        """Generate images from a prompt. See ``passthrough.images``."""
        return await passthrough.images(
            self, prompt, model=model, provider=provider, **extra)

    async def respond(
        self, prompt: str, *, model: str, **kwargs: Any,
    ) -> passthrough.Answer:
        """Ask through the ``responses`` route. See ``passthrough.respond``.

        **Check ``truncated``** on the answer: ``incomplete`` means the budget
        ran out, usually into thinking, and the text stops mid-sentence.
        """
        return await passthrough.respond(self, prompt, model=model, **kwargs)

    async def call(
        self, route: str, body: dict[str, Any], *, provider: str | None = None,
    ) -> dict[str, Any]:
        """Any other forwarded route. See ``passthrough.call``.

        The escape hatch, as ``repo.raw`` is on the edu-sharing side:
        ``await llm.call("audio/speech", {...})``.
        """
        return await passthrough.call(self, route, body, provider=provider)

    async def _pick(self, provider: str) -> Model:
        return pick_model(await self.models(provider))

    async def _request(
        self, method: str, path: str, *,
        max_retries: int | None = None, **kwargs: Any,
    ) -> Any:
        """One request, retried within the given budget.

        ``max_retries`` overrides the client's own budget for this call. The
        candidate loop in ``chat`` uses it to move on quickly while another
        model is still available -- see ``DEFAULT_RETRIES_BEFORE_SWITCHING``.
        """
        url = f"{self.base_url}{path}"
        last: EduSharingError | None = None
        budget = self.max_retries if max_retries is None else max_retries

        for attempt in range(budget + 1):
            if attempt:
                # No retry-after on the 429 -- exponential is all there is.
                await asyncio.sleep(self.backoff_base * (2 ** (attempt - 1)))
            try:
                async with self._semaphore:
                    response = await self._client.request(
                        method, url,
                        headers={"X-API-KEY": self._api_key,
                                 "Accept": "application/json"},
                        **kwargs,
                    )
            except httpx.HTTPError as exc:
                last = EduSharingError(f"{type(exc).__name__}: {exc}", url=url)
                continue

            if response.status_code < 400:
                return response.json()

            last = self._error(response, url)
            if response.status_code not in RETRYABLE:
                raise last

        # ``max_retries >= 0`` is checked in the constructor, so the loop runs
        # at least once and has set ``last`` on every branch that does not
        # itself return or raise. An assert here would vanish under ``python -O``
        # and turn into ``raise None`` -- a TypeError instead of the real cause.
        raise last  # type: ignore[misc]

    def _error(self, response: httpx.Response, url: str) -> EduSharingError:
        """Build an error from the b-api response.

        It reports under ``message``, not in the edu-sharing shape -- so the
        text is taken here rather than looked for there.
        """
        try:
            data = response.json()
            message = data.get("message") or data.get("error") or response.text
        except ValueError:
            message = response.text
        base = error_from_response(response.status_code, url, "")
        return type(base)(
            f"b-api HTTP {response.status_code}: {str(message)[:300]}",
            status=response.status_code, url=url,
        )

    def __repr__(self) -> str:
        return f"BildungsAPI(base_url={self.base_url!r}, provider={self.provider!r})"
