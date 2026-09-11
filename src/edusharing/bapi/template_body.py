"""What a template request looks like, and what the writing routes answer.

The shape, not the sending -- that is ``templates``, as ``body`` is for the
proxy. Input is checked before anything is sent, so a wrong argument is named
by its Python name instead of coming back as a server error.

Pure functions throughout, so all of it is testable without network access.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from ..errors import EduSharingError, ValidationError

__all__ = ["DEFAULT_USER", "Config", "NodeConfig", "Values"]

#: The placeholders ``user(...)`` read this account. The server insists on the
#: field; measured, none of the 22 configurations uses it, and ``guest``
#: carries no personal data.
DEFAULT_USER = "guest"


@dataclass(frozen=True)
class NodeConfig:
    """A configuration stored on a node, in ``ccm:bapi_config``, under a name.

    The other form -- a configuration in the metadata set -- is simply its id
    as a string, which is what all measured configurations are.
    """

    node_id: str
    config_name: str


#: A string is a configuration in the metadata set; ``NodeConfig`` one on a node.
Config = str | NodeConfig
#: ``{key: value}`` or ``{key: [values]}`` -- the server wants lists.
Values = Mapping[str, str | Sequence[str]]


def _config_refs(configs: Sequence[Config]) -> list[dict[str, str]]:
    """The configurations as the server wants them, checked first.

    A bare string is refused rather than read: ``chat("abc")`` would otherwise
    be three configurations ``a``, ``b`` and ``c`` -- three unknown ids sent
    without a word.
    """
    if isinstance(configs, str):
        raise ValidationError(
            f"configs must be a list of configurations, not the string "
            f"{configs!r} -- write [{configs!r}].")
    refs: list[dict[str, str]] = []
    for config in configs:
        if isinstance(config, NodeConfig) and config.node_id and config.config_name:
            refs.append({"type": "node", "nodeId": config.node_id,
                         "configName": config.config_name})
        elif isinstance(config, str) and config:
            refs.append({"type": "mds", "id": config})
        else:
            raise ValidationError(
                f"{config!r} is not a configuration: a non-empty id from the "
                "metadata set, or NodeConfig(node_id, config_name).")
    if not refs:
        raise ValidationError(
            "At least one configuration is needed -- the prompt lives in it.")
    return refs


def _as_lists(values: Values | None) -> dict[str, list[str]]:
    """``{key: value | [values]}`` as ``{key: [values]}``, strings only.

    Anything else would reach the prompt as ``str()`` of a Python object, or
    fail on the server with a deserialisation trace.
    """
    lists: dict[str, list[str]] = {}
    for key, value in (values or {}).items():
        items = ([value] if isinstance(value, str)
                 else list(value) if isinstance(value, Sequence) else [value])
        if not all(isinstance(item, str) for item in items):
            raise ValidationError(
                f"The value for {key!r} must be a string or a list of strings, "
                f"not {value!r}.")
        lists[key] = items
    return lists


def _pairs(choices: Values | None) -> list[dict[str, str]]:
    """``{widget: value | [values]}`` as the limited mode's list of pairs."""
    return [{"widgetId": widget, "valueId": value}
            for widget, values in _as_lists(choices).items()
            for value in values]


def _object(answer: Any, route: str) -> dict[str, Any]:
    """The object a reading route answers with -- or an error, never a guess.

    The parsers behind these routes read with ``.get()``: a list or a string
    reached them as an ``AttributeError``, which no ``except EduSharingError``
    catches (review 2026-09-11).
    """
    if not isinstance(answer, dict):
        raise EduSharingError(
            f"The b-api answered /{route} with {type(answer).__name__}, not an "
            "object -- there is no answer to read from it.")
    return answer


def _records(answer: Any, route: str) -> list[dict[str, Any]]:
    """The list a writing route answers with -- or an error, never a guess.

    Read as empty, an unexpected shape would say "nothing was stored" when the
    truth is "nobody can tell from this what was stored".
    """
    if not isinstance(answer, list) or not all(isinstance(e, dict) for e in answer):
        raise EduSharingError(
            f"The b-api answered /{route} with {type(answer).__name__}, not a list "
            "of records -- what was stored cannot be told from it.")
    return answer


def _required(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(
            f"{name} is required -- the b-api refuses a request without it "
            "(measured: 400).")
    return value


def _template_body(
    metadataset: str, configs: Sequence[Config], context_node_id: str, user: str,
    variables: Any,
) -> dict[str, Any]:
    return {
        "metadataSet": metadataset,
        "configIds": _config_refs(configs),
        "user": _required("user", user),
        "contextNodeId": _required("context_node_id", context_node_id),
        "variables": variables,
    }
