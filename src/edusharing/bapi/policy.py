"""Model choice and request shape for the b-api -- the rules, without the network.

Separate from the client because this is where the actual knowledge sits: which
model family requires which body layout, and which model to use right now. As
pure functions both are testable without network access.

The quirks are not optional. All were measured against the b-api:

* **The GPT-5 and o series** need ``max_completion_tokens`` instead of
  ``max_tokens`` and reject a deviating ``temperature`` -- otherwise 400.
* **Qwen3** gets thinking switched off through ``chat_template_kwargs``, worth
  a factor of 7 to 9 (17.33 s versus 1.96 s on the same task). ``/no_think`` in
  the prompt does **not** work -- that is Qwen2.5 syntax.
* **Mistral rejects the very same flag with 400**
  (``chat_template is not supported for Mistral tokenizers``). Sending it
  generically is exactly where you fall over.
* **Reasoning models count their thinking.** Once the budget is spent,
  ``content`` is null and the text sits in ``reasoning``.

``demand`` is the only load information available, and it predicts waiting time
well: measured below 0.6 s at 0 and 30 to 41 s at 5. The scale is undocumented
by GWDG and open-ended.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = ["Model", "pick_model", "rank_models", "build_body", "read_answer"]

#: Model families with a deviating body layout.
_MAX_COMPLETION_PREFIXES = ("gpt-5", "o1", "o3", "o4")
_THINKING_PREFIXES = ("qwen3",)
_NO_CHAT_TEMPLATE = ("mistral",)

DEFAULT_MAX_TOKENS = 1000


@dataclass(frozen=True)
class Model:
    """A model as ``/models`` reports it."""

    id: str
    #: Load. ``None`` when the provider does not report it (OpenAI).
    demand: int | None = None
    status: str | None = None
    input: tuple[str, ...] = ()
    output: tuple[str, ...] = ()
    owned_by: str | None = None
    name: str | None = None

    @property
    def is_ready(self) -> bool:
        """Whether the model reports itself as usable.

        A provider without ``status`` (OpenAI) counts as ready -- the field is
        absent there, not negative.
        """
        return self.status is None or self.status == "ready"

    @property
    def can_chat(self) -> bool:
        """Whether it emits text.

        An embedding or audio model at ``/chat/completions`` answers with
        ``404 This is not a chat model``.
        """
        return not self.output or "text" in self.output

    @classmethod
    def from_response(cls, data: dict[str, Any]) -> Model:
        return cls(
            id=data.get("id") or "",
            demand=data.get("demand"),
            status=data.get("status"),
            input=tuple(data.get("input") or ()),
            output=tuple(data.get("output") or ()),
            owned_by=data.get("owned_by"),
            name=data.get("name"),
        )


def rank_models(models: list[Model]) -> list[Model]:
    """All usable models, least loaded first.

    The whole ranking is needed, not just the first entry: measured,
    ``apertus-70b-instruct-2509`` reports ``status: ready`` and ``demand: 0``
    yet answers with ``503 Model pricing unavailable``. That a model is unusable
    appears in no model list -- you find out by asking, and then you need a
    successor.
    """
    usable = [m for m in models if m.is_ready and m.can_chat]
    # Sort demand None (providers without load info) last, so a measured value
    # is preferred over a missing one.
    return sorted(usable, key=lambda m: (m.demand if m.demand is not None else 99, m.id))


def pick_model(models: list[Model], *, prefer: str | None = None) -> Model:
    """Choose a model -- the least loaded one that can answer.

    Args:
        prefer: the wanted model id. If it is not in the list, that is reported
            rather than silently switching to another model. Model ids change
            without notice -- ``deepseek-v4-flash`` became
            ``deepseek-v4-flash-0731`` within nine days, and the old name has
            answered 503 ever since. A silent switch would be worse than an
            error: the answer would come from a different model without anyone
            noticing.

    Raises:
        ValueError: when ``prefer`` is absent or no model is usable.
    """
    if prefer:
        for m in models:
            if m.id == prefer:
                return m
        available = ", ".join(m.id for m in models) or "(none)"
        raise ValueError(
            f"Model {prefer!r} does not exist here. Available: {available}. "
            "Model ids change without notice -- check against /models before "
            "hard-coding one."
        )

    ranking = rank_models(models)
    if not ranking:
        raise ValueError(
            f"No ready text model among the {len(models)} reported."
        )
    return ranking[0]


def build_body(
    model: str,
    messages: list[dict[str, str]],
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = 0.0,
    thinking: bool = False,
    stream: bool = False,
) -> dict[str, Any]:
    """Build the request body for the model family of ``model``.

    Args:
        thinking: ``True`` lets Qwen3 think. The default is ``False`` because
            it costs a factor of 7 to 9 and buys nothing for extraction or
            classification.
    """
    key = model.lower()
    body: dict[str, Any] = {"model": model, "messages": messages}

    if key.startswith(_MAX_COMPLETION_PREFIXES):
        body["max_completion_tokens"] = max_tokens
        # temperature deliberately omitted -- this family rejects a deviating
        # value with 400.
    else:
        body["max_tokens"] = max_tokens
        body["temperature"] = temperature

    if (
        not thinking
        and key.startswith(_THINKING_PREFIXES)
        and not any(k in key for k in _NO_CHAT_TEMPLATE)
    ):
        body["chat_template_kwargs"] = {"enable_thinking": False}

    if stream:
        body["stream"] = True
        # Without include_usage the final event carries no usage, and waiting
        # time cannot be told apart from generation time.
        body["stream_options"] = {"include_usage": True}

    return body


def read_answer(response: dict[str, Any]) -> str:
    """Read the answer text.

    Checks ``content`` **and** ``reasoning``: if the token budget went into
    thinking, ``content`` is null and the text sits in the second field. Reading
    only ``content`` yields nothing there.
    """
    choices = response.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    return str(message.get("content") or message.get("reasoning") or "")
