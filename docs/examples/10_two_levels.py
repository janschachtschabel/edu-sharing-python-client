"""The same use case, written twice: API level and flow level.

    EDU_SHARING_USER=... EDU_SHARING_PASSWORD=... \
        python docs/examples/10_two_levels.py

Creates a throwaway folder of its own and removes it afterwards. Nothing that
was already there is touched.

Neither level is the "advanced" one. They answer different questions:

* The **API level** returns objects. `Node` has `update()`, `add_keywords()`,
  `content.upload()` — you keep working with what you got back.
* The **flow level** returns `dict`. That is what an MCP tool, an HTTP endpoint
  or a prompt needs, and it is a dead end for further work in Python.

This script counts the requests each version sends, so the cost is visible
rather than asserted. Run it and compare the two columns.
"""

import sys
import uuid

import httpx

from edusharing import EduSharingError, Node, NotFoundError, Repository

# The Windows console otherwise emits cp1252 and mangles umlauts.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REQUESTS: list[str] = []


class Counting(httpx.AsyncHTTPTransport):
    """Logs every request so the two versions can be compared honestly."""

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path.replace("/edu-sharing/rest", "")
        REQUESTS.append(f"{request.method} {path}")
        return await super().handle_async_request(request)


def show(title: str) -> None:
    print(f"  {title}: {len(REQUESTS)} requests")
    for entry in REQUESTS:
        print(f"      {entry}")
    REQUESTS.clear()


def fresh(repo: Repository) -> None:
    """Clear the vocabulary cache before a comparison.

    Without this the second version looks cheaper than it is: the first one
    already fetched the vocabulary, and a cached lookup sends nothing. That is
    a real saving in production and a measurement error here.
    """
    repo.vocab.clear_cache()
    REQUESTS.clear()


def compare_search(repo: Repository) -> None:
    """Find material about photosynthesis, subject biology -- both ways."""
    print("\nUse case: find material about photosynthesis, subject biology")
    print("=" * 72)

    # API level — objects come back, you filter and inspect them yourself.
    fresh(repo)
    result = repo.search("Photosynthese", subject="Biologie", limit=3)
    api_titles = [h.title for h in result.hits]
    # Readable values need the _DISPLAYNAME convention, which you have to know:
    api_subjects = result.hits[0].labels("ccm:taxonid")
    show("API level  repo.search(...)")

    # Flow level — a dict comes back, ready to hand on.
    fresh(repo)
    flow = repo.flows.search("Photosynthese", subject="Biologie", limit=3)
    flow_titles = [h["title"] for h in flow["hits"]]
    flow_subjects = flow["hits"][0]["fields"].get("subject", [])
    show("Flow level repo.flows.search(...)")

    print(f"  subject via API : {api_subjects}  (you had to know _DISPLAYNAME)")
    print(f"  subject via flow: {flow_subjects}  (keyed by your short name)")
    overlap = len(set(api_titles) & set(flow_titles))
    print(f"  titles in common: {overlap} of {len(api_titles)}")
    if overlap < len(api_titles):
        print("     not a difference between the levels -- the index itself")
        print("     returns different candidates for identical queries.")
    print("  -> same requests, same shape of work. The flow changes the")
    print("     output format, not what is asked of the repository.")


def compare_create(repo: Repository, folder: Node) -> None:
    """Create material with a subject -- both ways."""
    print("\nUse case: create material with a subject, in your home folder")
    print("=" * 72)

    # API level — three steps you have to know about and get right.
    fresh(repo)
    uri = repo.resolve("ccm:taxonid", "Biologie")       # label -> URI
    node = repo.create_node(
        folder.id,
        name="api-level-material",                       # derive it yourself
        title="Written at the API level",
        properties={"ccm:taxonid": [uri]},
    )
    show("API level  resolve + create_node")

    # Flow level — one call. Same work, and it reports what did not resolve
    # instead of writing material that looks tagged and is not.
    fresh(repo)
    created = repo.flows.add_material(
        "Written at the flow level",
        parent_id=folder.id,
        subject="Biologie",
    )
    show("Flow level repo.flows.add_material(...)")

    print(f"  both created: {bool(node.id)} / {bool(created['id'])}")
    print(f"  unresolved reported by the flow: {created['unresolved'] or 'none'}")
    print("  -> same requests again, but the flow resolves the vocabulary")
    print("     and names what fell through. Writing it by hand means")
    print("     knowing that ccm:taxonid wants a URI, and noticing when")
    print("     the label had no match.")


def show_saved_round_trip(repo: Repository, folder: Node) -> None:
    """Where a flow genuinely saves calls, rather than only reshaping them."""
    print("\nWhere a flow really does save calls")
    print("=" * 72)
    repo.flows.collection_contents(folder.id, limit=5)
    show("Flow level collection_contents (2 requests, in parallel)")
    print("  -> written by hand these are two awaits one after the other;")
    print("     the flow runs them at once and merges the answer.")


def show_mixing(repo: Repository) -> None:
    """Flows to get data out, the API level to keep working with it."""
    print("\nMixing is the normal case")
    print("=" * 72)
    found = repo.flows.search("Wald", subject="Biologie", limit=5)  # JSON out
    for hit in found["hits"]:
        try:
            node = repo.node(hit["id"])                              # object back
        except NotFoundError:
            # Not a contrived case: the index holds records whose node is gone.
            # Measured 2026-08-27, 4 of 25. Anything chaining a search to a
            # lookup has to survive it -- this example did not, at first.
            print(f"  indexed but gone, skipping: {hit['id'][:8]}")
            continue
        print(f"  found as JSON, then loaded as an object: {node.title[:50]}")
        print(f"  now usable: node.can_write = {node.can_write}")
        break
    else:
        print("  no retrievable hit among the five -- unusual, but possible")
    print("  -> flows to get data out, the API level to keep working with it.")


def main() -> int:
    client = httpx.AsyncClient(transport=Counting(), timeout=30.0)
    with Repository.from_env(metadataset="mds_oeh", client=client) as repo:
        who = repo.whoami()
        if who.is_anonymous:
            print("Sign in first: set EDU_SHARING_USER and EDU_SHARING_PASSWORD.",
                  file=sys.stderr)
            return 1
        REQUESTS.clear()

        compare_search(repo)

        folder = repo.create_node(
            who.home_folder, name=f"example-two-levels-{uuid.uuid4().hex[:8]}",
            type="cm:folder")
        REQUESTS.clear()
        try:
            compare_create(repo, folder)
            show_saved_round_trip(repo, folder)
        finally:
            folder.delete(recycle=False)

        show_mixing(repo)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
