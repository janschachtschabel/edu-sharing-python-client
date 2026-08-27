"""Bausteine fuer KI-Anwendungen auf dieser Bibliothek.

Framework-neutral: kein MCP-, kein LangChain-Import. Was hier liegt, sind die
Teile, die ein Dienst braucht, der Repositoriums-Inhalte an ein Sprachmodell
weiterreicht -- und die ein reiner API-Client nicht mitbringt.
"""

from .safety import UnsafeUrlError, check_url, is_safe_url

__all__ = ["is_safe_url", "check_url", "UnsafeUrlError"]
