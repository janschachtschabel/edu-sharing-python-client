"""A node's binary content: upload, download, read text.

Its own module and its own object (``node.content``), because files answer a
different question than metadata -- and because ``Node`` would otherwise keep
growing.

Four quirks, measured against edu-sharing 11.0 (staging, 2026-08-27):

* **There is no ``GET .../content``.** The path exists only as a ``POST`` for
  uploading; a GET on it answers ``405``. Downloading goes through the
  ``downloadUrl`` from the node's metadata.
* **``downloadUrl`` says nothing about whether content exists.** It is always
  set, and a node without a file answers ``200`` with zero bytes there. The
  reliable signal is ``content.hash``: measured, it is ``None`` only when there
  is no content -- for a 0-byte file it is set. ``cclom:size`` is no good for
  this, since the empty file also has ``None`` there.
* **``mimetype`` is mandatory on upload** -- the specification declares it as
  required.
* **``textContent`` answers with JSON**, not with the text: the body is
  ``{"text": ...}``.

The full text carries a limitation an application should pass on to its users:
for linked resources, extraction is URL-driven. The transformation service
fetches ``ccm:wwwurl``; whatever is sent to ``textContent`` via ``POST`` lands
as binary content that nobody reads. For a non-crawlable resource the full text
therefore cannot be stored -- which should be said, rather than reporting
success.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .errors import EduSharingError, ValidationError

if TYPE_CHECKING:
    from .nodes import Node

__all__ = ["NodeContent"]


class NodeContent:
    """Access to a node's binary content."""

    def __init__(self, node: Node) -> None:
        self._node = node

    @property
    def _transport(self) -> Any:
        return self._node._nodes.transport

    @property
    def download_url(self) -> str | None:
        """The address of the binary content.

        Always set -- it does **not** prove that content exists. That is what
        ``has_content`` is for.
        """
        return self._node.raw.get("downloadUrl") or None

    @property
    def has_content(self) -> bool:
        """Whether the node carries a file.

        Checked on the hash: measured, it is ``None`` without content and set
        for a 0-byte file. A download without content otherwise returns zero
        bytes without complaint, indistinguishable from an empty file.
        """
        return bool((self._node.raw.get("content") or {}).get("hash"))

    @property
    def mimetype(self) -> str | None:
        return self._node.raw.get("mimetype")

    @property
    def size(self) -> int | None:
        """Size in bytes, where the repository reports it."""
        value = self._node.get("cclom:size")
        return int(value) if value and str(value).isdigit() else None

    async def upload(
        self,
        data: bytes,
        *,
        filename: str,
        mimetype: str,
        version_comment: str | None = None,
    ) -> Node:
        """Upload bytes as the node's content.

        Args:
            data: the file content.
            filename: name in the multipart part.
            mimetype: mandatory -- without it the repository cannot classify the
                content.
            version_comment: note for the version history.

        Returns:
            The freshly loaded node -- size and mimetype are only settled
            afterwards.

        Raises:
            ValidationError: when ``mimetype`` is missing.
        """
        if not mimetype:
            raise ValidationError(
                "mimetype is mandatory on upload (e.g. 'application/pdf' or "
                "'text/plain')."
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
        """Fetch the binary content.

        Raises:
            EduSharingError: when the node carries no file -- a link record, for
                instance. Returning an empty bytestring would be
                indistinguishable from an empty file.
        """
        url = self.download_url
        if not self.has_content or not url:
            raise EduSharingError(
                f"Node {self._node.id} carries no file. A download would return "
                "zero bytes without complaint, indistinguishable from an empty "
                "file. For a link record the source is in ccm:wwwurl "
                "(node.get('ccm:wwwurl'))."
            )
        response = await self._transport.request("GET", url)
        return response.content

    async def text(self, *, force_update: bool = False) -> str:
        """The extracted full text.

        Requesting it triggers the extraction itself; ``force_update`` forces it
        again. For linked resources the outcome depends on whether the source is
        reachable -- see the module docstring.

        Returns:
            The text, or an empty string when there is none.
        """
        params = {"forceUpdate": "true"} if force_update else None
        response = await self._transport.json(
            "GET",
            f"/node/v1/nodes/-home-/{self._node.id}/textContent",
            params=params,
        )
        if isinstance(response, dict):
            return str(response.get("text") or "")
        return str(response or "")

    def __repr__(self) -> str:
        return f"NodeContent(node={self._node.id!r}, mimetype={self.mimetype!r})"
