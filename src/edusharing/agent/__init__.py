"""Building blocks for AI applications on top of this library.

Framework-neutral: no MCP, no LangChain import. What lives here are the parts a
service needs when it passes repository content to a language model -- and that
a plain API client does not bring along.

* ``safety``   -- may this URL be fetched? (SSRF)
* ``sanitize`` -- prepare foreign content for a model context
* ``format``   -- hits, compact, budgeted, without losing the citation
* ``result``   -- errors as results rather than exceptions
* ``confirm``  -- show what would happen, then do it
"""

from .confirm import ChangePlan, plan_update
from .format import cap_text, format_hit, format_results
from .result import ToolResult, as_result
from .safety import UnsafeUrlError, check_url, is_safe_url
from .sanitize import UNTRUSTED_MARKER, as_untrusted, sanitize_text

__all__ = [
    # URL checking
    "is_safe_url",
    "check_url",
    "UnsafeUrlError",
    # Foreign content
    "sanitize_text",
    "as_untrusted",
    "UNTRUSTED_MARKER",
    # Rendering
    "format_hit",
    "format_results",
    "cap_text",
    # Tool results
    "ToolResult",
    "as_result",
    # Present before executing
    "ChangePlan",
    "plan_update",
]
