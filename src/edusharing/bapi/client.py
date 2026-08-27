"""Access to the b-api, the LLM gateway of OpenEduHub.

Measured against staging:

* **Auth via ``X-API-KEY``**, not Bearer -- the mirror image of edu-sharing,
  where Basic applies and a Bearer is ignored.
* **Two providers**: ``academiccloud`` (with the ``demand`` load figure) and
  ``openai`` (without). A third name ends in ``400 Provider ... not found``.
* **No quota headers and no ``retry-after``.** A client cannot see its
  remaining allowance and notices a limit only when it fails; exponential
  backoff is all that is possible.
* **No OpenAPI document.** ``/openapi.json``, ``/docs`` and ``/health`` all
  serve the Angular frontend. You have to know the endpoints.

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
from typing import Any, Self

import httpx

from ..errors import EduSharingError, at_least, error_from_response
from ..urls import path_segment
from .policy import Model, build_body, pick_model, rank_models, read_answer

__all__ = ["BildungsAPI"]

#: See ``edusharing.transport.logger``. Under automatic model selection this is
#: the only place that says which candidates were tried and why they failed.
logger = logging.getLogger(__name__)

ENV_KEY = "B_API_KEY"
ENV_BASE_URL = "B_API_BASE_URL"

DEFAULT_BASE_URL = "https://b-api.staging.openeduhub.net"
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
            disables the cache.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        provider: str = DEFAULT_PROVIDER,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
        backoff_base: float = DEFAULT_BACKOFF_BASE,
        models_cache_seconds: float = DEFAULT_MODELS_CACHE_SECONDS,
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
        self._api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.provider = provider
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.models_cache_seconds = models_cache_seconds
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
        """Build a client from ``B_API_KEY`` and optionally ``B_API_BASE_URL``."""
        key = os.environ.get(ENV_KEY, "")
        if not key:
            raise EduSharingError(
                f"{ENV_KEY} is not set. Either set the variable or pass the key: "
                "BildungsAPI(api_key=...)."
            )
        kwargs.setdefault("base_url", os.environ.get(ENV_BASE_URL) or DEFAULT_BASE_URL)
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
        now = time.monotonic()

        if (
            self.models_cache_seconds > 0
            and self._models_cache
            and which == self.provider
            and now - self._models_cache[0] < self.models_cache_seconds
        ):
            return self._models_cache[1]

        async with self._models_lock:
            response = await self._request("GET", f"/api/v1/llm/{path_segment(which)}/models")
            raw = response.get("data") if isinstance(response, dict) else response
            models = [Model.from_response(m) for m in (raw or [])]
            if which == self.provider:
                self._models_cache = (now, models)
            return models

    async def chat(
        self,
        prompt: str | list[dict[str, str]],
        *,
        model: str | None = None,
        provider: str | None = None,
        max_tokens: int = 1000,
        temperature: float = 0.0,
        thinking: bool = False,
        system: str | None = None,
    ) -> str:
        """Send a request and return the answer text.

        Args:
            prompt: a string or a ready message list.
            model: fixed model id. Without it the model list is fetched and the
                least loaded ready text model is chosen -- that costs an extra
                request but decides on current numbers.
            system: system message; effective only when ``prompt`` is a string.
            thinking: allow Qwen3 to think. Defaults to ``False`` -- see
                ``policy``.

        Returns:
            The answer text. If the budget went into thinking, the text comes
            from ``reasoning`` rather than ``content``.
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
            )

        if model:
            self.last_model = model
            return read_answer(await self._request("POST", path, json=body_for(model)))

        candidates = rank_models(await self.models(which))
        if not candidates:
            raise EduSharingError(f"No ready text model at provider {which!r}.")

        failures: list[str] = []
        for candidate in candidates[:DEFAULT_MODEL_ATTEMPTS]:
            try:
                response = await self._request("POST", path, json=body_for(candidate.id))
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
            self.last_model = candidate.id
            return read_answer(response)

        raise EduSharingError(
            "None of the models tried answered. " + " | ".join(failures)
        )

    async def _pick(self, provider: str) -> Model:
        return pick_model(await self.models(provider))

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}{path}"
        last: EduSharingError | None = None

        for attempt in range(self.max_retries + 1):
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
        raise last

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
