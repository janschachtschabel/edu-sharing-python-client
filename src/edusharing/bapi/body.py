"""What the request body has to look like, per model family.

The shape, not the choice -- that is ``models``. Nothing here knows what a
model list looks like; every function takes the model id as a plain string.

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
* **``responses`` wants the two reasoning parameters nested** and refuses the
  flat spelling that ``chat/completions`` requires.

Pure functions throughout, so all of it is testable without network access.
"""

from __future__ import annotations

from typing import Any

from ..errors import ValidationError

__all__ = [
    "build_body", "read_answer", "reasoning_for_responses",
    "DEFAULT_EFFORT", "DEFAULT_MAX_TOKENS", "DEFAULT_VERBOSITY",
    "UNSET", "ReasoningParam",
]

#: Model families with a deviating body layout.
_MAX_COMPLETION_PREFIXES = ("gpt-5", "o1", "o3", "o4")
_THINKING_PREFIXES = ("qwen3",)
_NO_CHAT_TEMPLATE = ("mistral",)

#: Families that accept ``reasoning_effort`` and ``verbosity``. The same
#: prefixes as above today, but for a different reason -- body layout there,
#: reasoning capability here -- so they are named separately and may diverge.
#: Measured 2026-08-31: ``gpt-5.6-luna`` and ``gpt-5-nano`` take both;
#: ``gpt-4o-mini`` and ``gpt-3.5-turbo`` answer 400.
_REASONING_PREFIXES = ("gpt-5", "o1", "o3", "o4")

DEFAULT_MAX_TOKENS = 1000

#: The default effort and verbosity. Low, because it is measurably cheaper:
#: ``gpt-5.6-luna`` spent 14 reasoning tokens without the parameter and 0 with
#: ``low`` on the same question (measured 2026-08-31).
DEFAULT_EFFORT = "low"
DEFAULT_VERBOSITY = "low"


class _Vorgabe:
    """Marks "the library's own default", distinguishable from a caller's value.

    The distinction carries a rule: a default may be dropped where the model
    does not know it, a caller's explicit value may not. Silently dropping the
    second would make an answer produced with low effort look exactly like one
    produced with high effort.
    """

    def __repr__(self) -> str:  # pragma: no cover - for error messages only
        return "<library default>"


#: Sentinel for "not chosen by the caller". ``None`` means "do not send it".
UNSET = _Vorgabe()

#: What ``reasoning_effort`` and ``verbosity`` accept. Three states, not two:
#: a value the caller chose, ``None`` for "do not send it", and ``UNSET`` for
#: "the library decides". Only the third may be dropped for an older model.
ReasoningParam = str | _Vorgabe | None


def _reasoning_param(
    body: dict[str, Any], name: str, wert: Any, model: str, *, vorgabe: str
) -> None:
    """Put one reasoning parameter into the body, or account for why not.

    Raises:
        ValidationError: when the caller asked for a value this model does
            not take. Not a plain ValueError: the library's promise is that
            every failure is an EduSharingError.
    """
    if wert is None:
        return
    kann = model.lower().startswith(_REASONING_PREFIXES)
    if isinstance(wert, _Vorgabe):
        # A default: apply it where it works, drop it silently where it does
        # not. That is what makes it a default rather than a request.
        if kann:
            body[name] = vorgabe
        return
    if not kann:
        raise ValidationError(
            f"Model {model!r} does not take {name}={wert!r} -- it answers 400. "
            f"Only the {', '.join(_REASONING_PREFIXES)} families accept it. "
            f"Pass {name}=None to leave it out, or choose a model that takes it. "
            "It is not dropped for you: an answer produced without it would be "
            "indistinguishable from one produced with it."
        )
    body[name] = wert


def reasoning_for_responses(
    model: str,
    *,
    reasoning_effort: ReasoningParam = UNSET,
    verbosity: ReasoningParam = UNSET,
) -> dict[str, Any]:
    """The same two parameters in the shape the ``responses`` route wants.

    ``chat/completions`` takes ``reasoning_effort`` and ``verbosity`` flat.
    ``responses`` refuses exactly those and wants ``reasoning={"effort": ...}``
    and ``text={"verbosity": ...}`` -- measured 2026-08-31, the flat form
    answers *"Unsupported parameter: 'reasoning_effort'. In the Responses
    API, ..."*.

    Same rule as everywhere: a default is dropped where the model cannot take
    it, a caller's value raises instead.

    Raises:
        ValidationError: as in ``build_body``.
    """
    flach: dict[str, Any] = {}
    _reasoning_param(flach, "reasoning_effort", reasoning_effort, model,
                     vorgabe=DEFAULT_EFFORT)
    _reasoning_param(flach, "verbosity", verbosity, model,
                     vorgabe=DEFAULT_VERBOSITY)

    verschachtelt: dict[str, Any] = {}
    if "reasoning_effort" in flach:
        verschachtelt["reasoning"] = {"effort": flach["reasoning_effort"]}
    if "verbosity" in flach:
        verschachtelt["text"] = {"verbosity": flach["verbosity"]}
    return verschachtelt


def build_body(
    model: str,
    messages: list[dict[str, str]],
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = 0.0,
    thinking: bool = False,
    stream: bool = False,
    reasoning_effort: ReasoningParam = UNSET,
    verbosity: ReasoningParam = UNSET,
) -> dict[str, Any]:
    """Build the request body for the model family of ``model``.

    Args:
        thinking: ``True`` lets Qwen3 think. The default is ``False`` because
            it costs a factor of 7 to 9 and buys nothing for extraction or
            classification.
        reasoning_effort: ``low``, ``medium`` or ``high`` for the GPT-5 and o
            series. Left unset it defaults to ``low``, which is applied only
            where the model takes it. ``None`` leaves it out entirely.
        verbosity: how long the answer should be, same families, same rule.

    Raises:
        ValidationError: when a caller's explicit ``reasoning_effort`` or
            ``verbosity`` goes to a model that does not accept it.
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

    _reasoning_param(body, "reasoning_effort", reasoning_effort, model,
                     vorgabe=DEFAULT_EFFORT)
    _reasoning_param(body, "verbosity", verbosity, model,
                     vorgabe=DEFAULT_VERBOSITY)

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
