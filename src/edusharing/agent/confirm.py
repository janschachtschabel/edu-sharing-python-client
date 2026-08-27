"""Erst zeigen, was passieren wuerde -- dann tun.

Ein Agent, der im Namen einer Person schreibt, muss die Aenderung vorlegen
koennen, bevor sie stattfindet. Sonst bleibt der Person nur, dem Modell zu
glauben, und der Unterschied zwischen "Titel ergaenzt" und "Titel ersetzt"
faellt erst am Ergebnis auf.

``plan_update`` liest den Ist-Zustand, vergleicht ihn mit dem Soll und schreibt
**nichts**. Erst ``apply()`` fuehrt aus -- ueber ``Node.update`` und damit
einschliesslich der Rueckleseprobe.

Zwei Dinge macht der Plan sichtbar, die sonst erst hinterher auffallen:
Aenderungen, die gar keine sind (gleicher Wert -- ein Schreibvorgang darauf
erzeugt nur eine Version), und ein fehlendes Schreibrecht.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..nodes import Node
from .sanitize import sanitize_text

__all__ = ["ChangePlan", "plan_update"]


def _zeige(werte: list[str], *, max_chars: int = 80) -> str:
    """Werte lesbar machen -- der Ist-Wert ist Fremdtext aus dem Repositorium."""
    if not werte:
        return "(leer)"
    text = ", ".join(sanitize_text(w) for w in werte)
    return text if len(text) <= max_chars else text[: max_chars - 1] + "…"


@dataclass
class ChangePlan:
    """Eine vorbereitete, noch nicht ausgefuehrte Aenderung."""

    node: Node
    #: ``{property: (ist, soll)}`` -- nur die Felder, die sich unterscheiden.
    changes: dict[str, tuple[list[str], list[str]]] = field(default_factory=dict)
    #: Felder, deren Sollwert dem Istwert entspricht.
    unchanged: dict[str, list[str]] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(self.changes)

    @property
    def can_write(self) -> bool:
        """Ob das Konto an diesem Knoten schreiben darf."""
        return self.node.can_write

    def describe(self) -> str:
        """Was dieser Plan aendern wuerde, als Text zum Vorlegen."""
        zeilen = [f"Knoten {self.node.id} ({sanitize_text(self.node.title) or 'ohne Titel'})"]

        if not self.can_write:
            zeilen.append(
                "! Kein Schreibrecht an diesem Knoten -- die Aenderung wuerde "
                "fehlschlagen oder stillschweigend verworfen."
            )

        if not self.changes:
            zeilen.append("Keine Aenderung: alle Werte stehen bereits so.")
            return "\n".join(zeilen)

        zeilen.append(f"{len(self.changes)} Aenderung(en):")
        for prop, (ist, soll) in self.changes.items():
            zeilen.append(f"  {prop}: {_zeige(ist)}  ->  {_zeige(soll)}")
        if self.unchanged:
            zeilen.append(f"  (unveraendert: {', '.join(sorted(self.unchanged))})")
        return "\n".join(zeilen)

    async def apply(self, *, verify: bool = True) -> Node:
        """Fuehre die Aenderung aus.

        Ohne Aenderung wird nicht geschrieben -- ein Schreibvorgang auf
        gleiche Werte erzeugt nur Last und moeglicherweise eine Version.

        Returns:
            Den zurueckgelesenen Knoten.

        Raises:
            SilentDropError: wie bei ``Node.update``.
        """
        if not self.changes:
            return self.node
        return await self.node.update(
            properties={prop: soll for prop, (_, soll) in self.changes.items()},
            verify=verify,
        )

    def __repr__(self) -> str:
        return f"ChangePlan(node={self.node.id!r}, changes={len(self.changes)})"


async def plan_update(
    node: Node,
    *,
    properties: dict[str, Any] | None = None,
    **aliases: Any,
) -> ChangePlan:
    """Bereite eine Aenderung vor, ohne sie auszufuehren.

    Nimmt dieselben Argumente wie ``Node.update``. Der Sollzustand wird gegen
    den geladenen Istzustand gehalten; geschrieben wird nichts.

    Raises:
        ValidationError: bei einem unbekannten Kurznamen -- ein Tippfehler soll
            vor der Vorlage auffallen, nicht danach.
    """
    # Nutzt dieselbe Alias-Aufloesung wie update(), damit Plan und Ausfuehrung
    # nicht auseinanderlaufen koennen.
    soll = node._felder(properties, aliases)

    changes: dict[str, tuple[list[str], list[str]]] = {}
    unchanged: dict[str, list[str]] = {}
    for prop, neue_werte in soll.items():
        ist = node.get_all(prop)
        if ist == neue_werte:
            unchanged[prop] = ist
        else:
            changes[prop] = (ist, neue_werte)

    return ChangePlan(node=node, changes=changes, unchanged=unchanged)
