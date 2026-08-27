"""Knoten lesen, anlegen, aendern, loeschen -- mit Rueckleseprobe.

Der Grund, warum dieses Modul nicht duenn ist: **edu-sharing antwortet auf
verlorene Schreibvorgaenge mit HTTP 200.** Gemessen an einem Wegwerf-Knoten
(edu-sharing 11.0, Staging, 27.08.2026):

======================================  ====  ============
Vorgang                                 HTTP  gespeichert
======================================  ====  ============
``PUT /metadata``, Property im MDS       200  ja
``PUT /metadata``, Property nicht im MDS 200  **nein**
``POST /property``, dieselbe Property    200  ja
``PUT /metadata``, erfundenes Feld       200  **nein**
======================================  ====  ============

Zweimal ein Erfolgscode fuer etwas, das nicht passiert ist. Wer sich darauf
verlaesst, meldet seinen Nutzenden gespeicherte Daten, die es nicht gibt.

Deshalb liest ``update()`` nach jedem Schreibvorgang zurueck und wirft
``SilentDropError``, wenn ein Wert fehlt. Es gibt zwei uebliche Ursachen --
die Property ist im Metadatensatz nicht vorgesehen, oder das Schreibrecht
fehlt --, und beide sind aus der Antwort allein nicht unterscheidbar; die
Fehlermeldung nennt daher beide samt Ausweg.

Automatisch auf ``set_property`` auszuweichen waere bequem und falsch: die
Filterung des Metadatensatzes ist eine Entscheidung des Repositoriums, keine
Panne. Sie zu umgehen ist ein bewusster Schritt.
"""

from __future__ import annotations

from typing import Any

from .errors import SilentDropError, ValidationError
from .transport import Transport

__all__ = ["Node", "Nodes", "SyncNode", "WRITE_FIELD_ALIASES"]

#: Kurznamen fuer Schreibfelder. Titel und Beschreibung gehen bewusst in
#: **beide** Namensraeume: die edu-sharing-Oberflaeche rendert ``cm:*`` und
#: ``cclom:*`` an verschiedenen Stellen, und nur eines zu setzen fuehrt dazu,
#: dass die Anzeige etwas anderes zeigt als die Anwendung geschrieben hat.
WRITE_FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "titel": ("cm:title", "cclom:title"),
    "beschreibung": ("cm:description", "cclom:general_description"),
    "url": ("ccm:wwwurl",),
    "name": ("cm:name",),
    "autor": ("ccm:author_freetext",),
    "schlagworte": ("cclom:general_keyword",),
}

DEFAULT_NODE_TYPE = "ccm:io"


def _als_liste(wert: Any) -> list[str]:
    """edu-sharing erwartet jede Property als Liste, auch einzelne Werte."""
    if wert is None:
        return []
    if isinstance(wert, (list, tuple)):
        return [str(v) for v in wert]
    return [str(wert)]


class Node:
    """Ein geladener Knoten.

    Unveraenderlich: ``update()`` und ``set_property()`` geben einen **neuen**
    ``Node`` mit dem zurueckgelesenen Zustand zurueck, statt diesen hier zu
    veraendern. So kann kein Objekt behaupten, einen Wert zu tragen, den das
    Repositorium nie angenommen hat.
    """

    def __init__(self, data: dict[str, Any], nodes: Nodes) -> None:
        self._data = data
        self._nodes = nodes

    # --- Lesen ------------------------------------------------------------

    @property
    def id(self) -> str:
        return (self._data.get("ref") or {}).get("id") or ""

    @property
    def name(self) -> str:
        return self._data.get("name") or ""

    @property
    def title(self) -> str:
        return self._data.get("title") or self.get("cclom:title") or ""

    @property
    def type(self) -> str:
        return self._data.get("type") or ""

    @property
    def url(self) -> str:
        """Die Ansichts-URL -- das, was man weitergibt."""
        return f"{self._nodes.repository_url}/components/render/{self.id}"

    @property
    def access(self) -> list[str]:
        """Die eigenen Rechte an diesem Knoten."""
        return list(self._data.get("access") or [])

    @property
    def can_write(self) -> bool:
        """Ob Schreiben erlaubt ist.

        Vorab pruefbar -- sonst ist ein fehlendes Recht von einer Filterung
        des Metadatensatzes erst nach dem Schreibversuch zu unterscheiden.
        """
        return "Write" in self.access

    @property
    def properties(self) -> dict[str, Any]:
        return self._data.get("properties") or {}

    @property
    def raw(self) -> dict[str, Any]:
        return self._data

    def get(self, prop: str) -> str | None:
        """Der erste Wert einer Property, oder ``None``."""
        werte = self.properties.get(prop)
        if isinstance(werte, list):
            return str(werte[0]) if werte else None
        return str(werte) if werte else None

    def get_all(self, prop: str) -> list[str]:
        """Alle Werte einer Property."""
        return _als_liste(self.properties.get(prop))

    # --- Schreiben --------------------------------------------------------

    async def update(
        self,
        *,
        properties: dict[str, Any] | None = None,
        verify: bool = True,
        **aliases: Any,
    ) -> Node:
        """Aendere Properties und lies zurueck, ob es angekommen ist.

        Args:
            properties: ``{property: wert}``. Einzelwerte werden zu Listen.
            verify: Rueckleseprobe. Nur abschalten, wenn die zusaetzliche
                Anfrage je Schreibvorgang nachweislich stoert -- sie ist der
                einzige Beleg, dass etwas gespeichert wurde.
            **aliases: Kurznamen aus ``WRITE_FIELD_ALIASES``, etwa ``titel=``.

        Returns:
            Einen neuen ``Node`` mit dem zurueckgelesenen Zustand.

        Raises:
            SilentDropError: wenn das Repositorium 200 meldet und Werte danach
                fehlen.
            ValidationError: bei einem unbekannten Kurznamen.
        """
        felder = self._felder(properties, aliases)
        if not felder:
            return self

        await self._nodes.transport.json(
            "PUT", f"/node/v1/nodes/-home-/{self.id}/metadata", json=felder
        )
        if not verify:
            return self

        frisch = await self._nodes.get(self.id)
        frisch._pruefe(felder, weg="update")
        return frisch

    async def set_property(self, prop: str, value: Any, *, verify: bool = True) -> Node:
        """Setze eine einzelne Property am Metadatensatz vorbei.

        Der Weg fuer Felder, die der Metadatensatz nicht kennt -- und der
        Grund, warum ``update()`` nicht selbst dorthin ausweicht: die Filterung
        zu umgehen soll eine bewusste Entscheidung bleiben.

        Args:
            value: der Wert, oder ``None`` zum Loeschen.

        Raises:
            SilentDropError: wenn der Wert danach nicht gesetzt ist.
        """
        if value is None:
            # Gemessen: sowohl ein Body "null" als auch gar kein Body loeschen
            # die Property. Gesendet wird das explizite "null" -- es ist der
            # dokumentierte Weg, und ein fehlender Body ist eine Auslassung,
            # die eine andere Version anders auslegen kann.
            await self._nodes.transport.request(
                "POST",
                f"/node/v1/nodes/-home-/{self.id}/property",
                params={"property": prop},
                content=b"null",
                headers={"Content-Type": "application/json"},
            )
        else:
            await self._nodes.transport.request(
                "POST",
                f"/node/v1/nodes/-home-/{self.id}/property",
                params={"property": prop},
                json=_als_liste(value),
            )
        if not verify:
            return self

        frisch = await self._nodes.get(self.id)
        if value is None:
            return frisch
        frisch._pruefe({prop: _als_liste(value)}, weg="set_property")
        return frisch

    async def delete(self, *, recycle: bool = True) -> None:
        """Loesche den Knoten.

        Args:
            recycle: ``True`` legt ihn in den Papierkorb. Der Schalter wird
                immer explizit gesendet, nie der Server-Vorgabe ueberlassen.

        Note:
            Wiederherstellbarkeit ist im Moment des Loeschens nicht
            nachweisbar -- die Archivsuche antwortet unzuverlaessig. Ein
            geloeschter Knoten gilt daher als weg.
        """
        await self._nodes.transport.request(
            "DELETE",
            f"/node/v1/nodes/-home-/{self.id}",
            params={"recycle": "true" if recycle else "false"},
        )

    # --- intern -----------------------------------------------------------

    def _felder(
        self, properties: dict[str, Any] | None, aliases: dict[str, Any]
    ) -> dict[str, list[str]]:
        felder: dict[str, list[str]] = {
            p: _als_liste(w) for p, w in (properties or {}).items()
        }
        for name, wert in aliases.items():
            ziele = WRITE_FIELD_ALIASES.get(name)
            if ziele is None:
                bekannt = ", ".join(sorted(WRITE_FIELD_ALIASES))
                raise ValidationError(
                    f"Unbekanntes Feld {name!r}. Bekannt sind: {bekannt}. "
                    "Eine Property laesst sich auch direkt angeben: "
                    "properties={'ccm:...': 'Wert'}."
                )
            for ziel in ziele:
                felder[ziel] = _als_liste(wert)
        return felder

    def _pruefe(self, erwartet: dict[str, list[str]], *, weg: str) -> None:
        """Vergleiche den zurueckgelesenen Zustand mit dem Geschriebenen."""
        verloren = [
            prop for prop, werte in erwartet.items()
            if self.get_all(prop) != werte
        ]
        if not verloren:
            return

        ausweg = (
            "node.set_property(...) umgeht die Filterung des Metadatensatzes."
            if weg == "update"
            else "Pruefe node.can_write -- ohne Schreibrecht bleibt auch dieser Weg wirkungslos."
        )
        raise SilentDropError(
            f"Nicht gespeichert: {', '.join(verloren)} (HTTP 200, nach der "
            f"Rueckleseprobe abwesend oder abweichend). Zwei uebliche Ursachen: "
            f"die Property ist im Metadatensatz dieser Instanz nicht vorgesehen, "
            f"oder das Schreibrecht fehlt. {ausweg}",
            dropped=verloren,
            url=self.url,
        )

    def __repr__(self) -> str:
        return f"Node(id={self.id!r}, title={self.title!r})"


class Nodes:
    """Zugriff auf Knoten eines Repositoriums."""

    def __init__(self, transport: Transport) -> None:
        self.transport = transport

    @property
    def repository_url(self) -> str:
        return self.transport.repository_url

    async def get(self, node_id: str) -> Node:
        """Lade einen Knoten mit allen Properties."""
        antwort = await self.transport.json(
            "GET",
            f"/node/v1/nodes/-home-/{node_id}/metadata",
            params={"propertyFilter": "-all-"},
        )
        return Node(antwort.get("node") or {}, self)

    async def create(
        self,
        parent_id: str,
        *,
        name: str,
        type: str = DEFAULT_NODE_TYPE,
        properties: dict[str, Any] | None = None,
        rename_if_exists: bool = True,
        **aliases: Any,
    ) -> Node:
        """Lege einen Knoten unter ``parent_id`` an.

        Args:
            name: ``cm:name`` -- der Schluessel im Elternknoten. Pflicht, weil
                das Ergebnis sonst vom Server abhaengt statt vorhersagbar zu sein.
            type: Knotentyp, ``ccm:io`` fuer Material, ``cm:folder`` fuer Ordner.
            rename_if_exists: haengt bei Namenskollision einen Zaehler an, statt
                mit 409 zu scheitern.
            **aliases: Kurznamen aus ``WRITE_FIELD_ALIASES``.

        Raises:
            ValidationError: wenn ``name`` leer ist.
        """
        if not name or not name.strip():
            raise ValidationError(
                "Ein Knoten braucht einen name (cm:name) -- er ist der Schluessel "
                "im Elternknoten."
            )

        platzhalter = Node({}, self)
        felder = platzhalter._felder(properties, aliases)
        felder["cm:name"] = [name]

        antwort = await self.transport.json(
            "POST",
            f"/node/v1/nodes/-home-/{parent_id}/children",
            params={
                "type": type,
                "renameIfExists": "true" if rename_if_exists else "false",
            },
            json=felder,
        )
        return Node(antwort.get("node") or {}, self)

    def __repr__(self) -> str:
        return f"Nodes({self.repository_url!r})"


class SyncNode:
    """Ein Knoten fuer den synchronen Zugang.

    Reicht die Methoden von ``Node`` blockierend durch. Ausgeschrieben statt
    dynamisch erzeugt: die Namen sollen in der IDE auffindbar und die
    Signaturen lesbar bleiben.
    """

    def __init__(self, node: Node, loop: Any) -> None:
        self._node = node
        self._loop = loop

    # Lesende Zugriffe sind ohnehin synchron und werden durchgereicht.
    def __getattr__(self, name: str) -> Any:
        return getattr(self._node, name)

    def update(self, **kwargs: Any) -> SyncNode:
        """Wie ``Node.update``, blockierend."""
        return SyncNode(self._loop.run(self._node.update(**kwargs)), self._loop)

    def set_property(self, prop: str, value: Any, **kwargs: Any) -> SyncNode:
        """Wie ``Node.set_property``, blockierend."""
        return SyncNode(
            self._loop.run(self._node.set_property(prop, value, **kwargs)), self._loop
        )

    def delete(self, **kwargs: Any) -> None:
        """Wie ``Node.delete``, blockierend."""
        self._loop.run(self._node.delete(**kwargs))

    def __repr__(self) -> str:
        return f"SyncNode(id={self._node.id!r}, title={self._node.title!r})"
