"""Bausteine fuer KI-Anwendungen auf dieser Bibliothek.

Framework-neutral: kein MCP-, kein LangChain-Import. Was hier liegt, sind die
Teile, die ein Dienst braucht, der Repositoriums-Inhalte an ein Sprachmodell
weiterreicht -- und die ein reiner API-Client nicht mitbringt.

* ``safety``   -- darf diese URL abgerufen werden? (SSRF)
* ``sanitize`` -- Fremdinhalt fuer den Modellkontext aufbereiten
* ``format``   -- Treffer kompakt, mit Budget, ohne die Fundstelle zu verlieren
* ``result``   -- Fehler als Ergebnis statt als Ausnahme
* ``confirm``  -- erst zeigen, was passieren wuerde, dann tun
"""

from .confirm import ChangePlan, plan_update
from .format import cap_text, format_hit, format_results
from .result import ToolResult, as_result
from .safety import UnsafeUrlError, check_url, is_safe_url
from .sanitize import UNTRUSTED_MARKER, as_untrusted, sanitize_text

__all__ = [
    # URLs pruefen
    "is_safe_url",
    "check_url",
    "UnsafeUrlError",
    # Fremdinhalt
    "sanitize_text",
    "as_untrusted",
    "UNTRUSTED_MARKER",
    # Formatierung
    "format_hit",
    "format_results",
    "cap_text",
    # Werkzeug-Ergebnisse
    "ToolResult",
    "as_result",
    # Vorlegen statt ausfuehren
    "ChangePlan",
    "plan_update",
]
