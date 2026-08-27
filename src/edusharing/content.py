"""Der Binaerinhalt eines Knotens: hochladen, herunterladen, Text lesen.

Eigenes Modul und eigenes Objekt (``node.content``), weil Dateien eine andere
Frage beantworten als Metadaten -- und weil ``Node`` sonst weiter waechst.

Drei Eigenheiten, gemessen gegen edu-sharing 11.0 (Staging, 27.08.2026):

* **Es gibt kein ``GET .../content``.** Der Pfad existiert nur als ``POST``
  zum Hochladen; ein GET darauf antwortet mit ``405``. Heruntergeladen wird
  ueber die ``downloadUrl`` aus den Metadaten des Knotens.
* **``downloadUrl`` sagt nichts darueber, ob es einen Inhalt gibt.** Sie ist
  immer gesetzt, und ein Knoten ohne Datei liefert daran ``200`` mit null
  Bytes. Das verlaessliche Signal ist ``content.hash``: gemessen ist er nur
  ohne Inhalt ``None`` -- bei einer 0-Byte-Datei ist er gesetzt. ``cclom:size``
  taugt dafuer nicht, denn auch die leere Datei hat dort ``None``.
* **``mimetype`` ist beim Hochladen Pflicht** -- die Spezifikation deklariert
  ihn als required.
* **``textContent`` antwortet mit JSON**, nicht mit dem Text: der Rumpf ist
  ``{"text": ...}``.

Zum Volltext gehoert eine Einschraenkung, die eine Anwendung ihren Nutzenden
weitergeben sollte: die Extraktion ist bei verlinkten Inhalten URL-getrieben.
Der Transformationsdienst holt sich ``ccm:wwwurl``; was per ``POST`` an
``textContent`` geschickt wird, landet als Binaerinhalt, den niemand liest.
Fuer einen nicht crawlbaren Inhalt laesst sich der Volltext daher nicht
ablegen -- das gehoert gesagt, statt Erfolg zu melden.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .errors import EduSharingError, ValidationError

if TYPE_CHECKING:
    from .nodes import Node

__all__ = ["NodeContent"]


class NodeContent:
    """Zugriff auf den Binaerinhalt eines Knotens."""

    def __init__(self, node: Node) -> None:
        self._node = node

    @property
    def _transport(self) -> Any:
        return self._node._nodes.transport

    @property
    def download_url(self) -> str | None:
        """Die Adresse des Binaerinhalts.

        Immer gesetzt -- sie belegt **nicht**, dass es einen Inhalt gibt.
        Dafuer ist ``has_content`` zustaendig.
        """
        return self._node.raw.get("downloadUrl") or None

    @property
    def has_content(self) -> bool:
        """Ob der Knoten eine Datei traegt.

        Geprueft am Hash: gemessen ist er ohne Inhalt ``None`` und bei einer
        0-Byte-Datei gesetzt. Ein Download ohne Inhalt liefert sonst
        klaglos null Bytes, ununterscheidbar von einer leeren Datei.
        """
        return bool((self._node.raw.get("content") or {}).get("hash"))

    @property
    def mimetype(self) -> str | None:
        return self._node.raw.get("mimetype")

    @property
    def size(self) -> int | None:
        """Groesse in Bytes, sofern das Repositorium sie fuehrt."""
        wert = self._node.get("cclom:size")
        return int(wert) if wert and str(wert).isdigit() else None

    async def upload(
        self,
        data: bytes,
        *,
        filename: str,
        mimetype: str,
        version_comment: str | None = None,
    ) -> Node:
        """Lade Bytes als Inhalt des Knotens hoch.

        Args:
            data: der Dateiinhalt.
            filename: Name im Multipart-Teil.
            mimetype: Pflicht -- ohne ihn kann das Repositorium den Inhalt
                nicht einordnen.
            version_comment: Vermerk fuer die Versionshistorie.

        Returns:
            Den neu geladenen Knoten -- Groesse und Mimetype stehen erst
            danach fest.

        Raises:
            ValidationError: wenn ``mimetype`` fehlt.
        """
        if not mimetype:
            raise ValidationError(
                "mimetype ist beim Hochladen Pflicht (etwa 'application/pdf' "
                "oder 'text/plain')."
            )
        params: dict[str, Any] = {"mimetype": mimetype}
        if version_comment:
            params["versionComment"] = version_comment

        await self._transport.request(
            "POST",
            f"/node/v1/nodes/-home-/{self._node.id}/content",
            params=params,
            files={"file": (filename, data, mimetype)},
        )
        return await self._node._nodes.get(self._node.id)

    async def download(self) -> bytes:
        """Hole den Binaerinhalt.

        Raises:
            EduSharingError: wenn der Knoten keine Datei traegt -- ein
                Link-Datensatz etwa. Einen leeren Bytestring zurueckzugeben
                waere nicht unterscheidbar von einer leeren Datei.
        """
        url = self.download_url
        if not self.has_content or not url:
            raise EduSharingError(
                f"Knoten {self._node.id} traegt keine Datei. Der Download wuerde "
                "klaglos null Bytes liefern, ununterscheidbar von einer leeren "
                "Datei. Bei einem Link-Datensatz steht die Quelle in ccm:wwwurl "
                "(node.get('ccm:wwwurl'))."
            )
        antwort = await self._transport.request("GET", url)
        return antwort.content

    async def text(self, *, force_update: bool = False) -> str:
        """Den extrahierten Volltext.

        Der Abruf stoesst die Extraktion selbst an; ``force_update`` erzwingt
        sie erneut. Bei verlinkten Inhalten haengt das Ergebnis daran, ob die
        Quelle erreichbar ist -- siehe Modul-Docstring.

        Returns:
            Den Text, oder einen leeren String, wenn keiner vorliegt.
        """
        params = {"forceUpdate": "true"} if force_update else None
        antwort = await self._transport.json(
            "GET",
            f"/node/v1/nodes/-home-/{self._node.id}/textContent",
            params=params,
        )
        if isinstance(antwort, dict):
            return str(antwort.get("text") or "")
        return str(antwort or "")

    def __repr__(self) -> str:
        return f"NodeContent(node={self._node.id!r}, mimetype={self.mimetype!r})"
