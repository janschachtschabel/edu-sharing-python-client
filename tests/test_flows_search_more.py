"""Was der MCP der Suche mitgibt und die Bibliothek noch nicht kannte.

``excludeNodeIds`` -- schon gezeigte Treffer ueberspringen -- und Facetten mit
bis zu hundert Werten. Beides gab es auf API-Ebene (``facet_limit``) oder gar
nicht; der Ablauf ``search`` nahm weder das eine noch das andere an.

Ausschliessen heisst NACHLADEN: wer acht Treffer will und drei ausschliesst,
bekommt sonst fuenf. Also wird um die Zahl der Ausschluesse mehr angefordert
und danach gekuerzt -- gedeckelt, damit eine lange Ausschlussliste keine
Riesenseite anfordert.
"""

import json

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.errors import ValidationError
from edusharing.flows.rerank import search_reranked

REPO = "https://repo.test/edu-sharing"


def _knoten(node_id: str) -> dict:
    return {"ref": {"id": node_id}, "title": f"Treffer {node_id}", "type": "ccm:io",
            "properties": {"cclom:title": [f"Treffer {node_id}"],
                           "ccm:wwwurl": [f"https://x/{node_id}"]}}


class Instanz:
    def __init__(self, ids: list[str]) -> None:
        self.ids = ids
        self.koerper: list[dict] = []
        self.params: list[dict] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        if "/values" in request.url.path:
            return httpx.Response(200, json={"values": []})
        self.koerper.append(json.loads(request.content))
        self.params.append(dict(request.url.params))
        wieviele = int(request.url.params.get("maxItems", 10))
        seite = [_knoten(i) for i in self.ids[:wieviele]]
        return httpx.Response(200, json={
            "nodes": seite, "facets": [],
            "pagination": {"total": len(self.ids), "from": 0, "count": len(seite)}})

    def repo(self) -> AsyncRepository:
        return AsyncRepository(
            REPO, metadataset="mds_oeh", backoff_base=0.0,
            client=httpx.AsyncClient(transport=httpx.MockTransport(self.handler)))


async def test_ausgeschlossene_treffer_fehlen_und_die_seite_bleibt_voll():
    instanz = Instanz([f"n{i}" for i in range(20)])
    async with instanz.repo() as repo:
        got = await repo.flows.search("x", limit=5, exclude_ids=["n0", "n2"])
    ids = [h["id"] for h in got["hits"]]
    assert "n0" not in ids and "n2" not in ids
    assert len(ids) == 5, ids
    assert int(instanz.params[0]["maxItems"]) >= 7, "um die Ausschluesse mehr angefordert"
    assert got["query"]["exclude_ids"] == ["n0", "n2"]


async def test_ohne_ausschluss_aendert_sich_nichts():
    instanz = Instanz([f"n{i}" for i in range(20)])
    async with instanz.repo() as repo:
        got = await repo.flows.search("x", limit=5)
    assert len(got["hits"]) == 5
    assert int(instanz.params[0]["maxItems"]) == 5
    assert "exclude_ids" not in got["query"]


async def test_facet_limit_wird_durchgereicht():
    instanz = Instanz(["n1"])
    async with instanz.repo() as repo:
        await repo.flows.search("x", facets=["subject"], facet_limit=100)
    facetten = instanz.koerper[0]["facets"]
    assert facetten and facetten[0]["property"] == "ccm:taxonid"
    assert instanz.koerper[0].get("facetLimit") == 100 or \
        any(f.get("count") == 100 or f.get("limit") == 100 for f in facetten), instanz.koerper[0]


# --- Paket 5: der Reranker reicht Kurznamen als Filter weiter, nicht als Parameter

async def test_rerank_weist_einen_fremden_parameter_ab():
    """``offset`` ist kein Kurzname. Bisher landete er als Parameter in
    ``Search.search`` -- ein Verhalten, das niemand bestellt hatte."""
    instanz = Instanz(["n1"])
    async with instanz.repo() as repo:
        with pytest.raises(ValidationError):
            await search_reranked(repo, "x", offset=3)


async def test_rerank_reicht_einen_kurznamen_als_filter_weiter():
    instanz = Instanz(["n1", "n2"])
    async with instanz.repo() as repo:
        await repo.flows.search("Bruch rechnen", rerank=True, subject="http://x/080")
    assert any(k["property"] == "ccm:taxonid" for k in instanz.koerper[0]["criteria"])
