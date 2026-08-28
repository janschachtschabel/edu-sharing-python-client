"""Use case: one query for everything, then find out what a hit actually is.

    python docs/examples/12_flow_place.py

Reads only. Nothing is created, changed or deleted, so this runs anonymously —
sign in and you simply see more.

Two flows that belong together in practice:

* `search_all` asks the two questions a topic really raises — which resources
  exist, and which collections someone has already assembled about it.
* `placement` answers what a single hit is: where it lives, and who has
  curated it. A collection holds a *reference*, so those are different answers.
"""

import sys

from edusharing import (
    EduSharingError,
    NotFoundError,
    PermissionDeniedError,
    Repository,
)

# The Windows console otherwise emits cp1252 and mangles umlauts.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

QUERY = "Photosynthese"


def search_both(repo: Repository) -> dict:
    """Material and collections in one call -- three requests, sent together."""
    result = repo.flows.search_all(QUERY, limit=5)
    materials, collections = result["materials"], result["collections"]

    print(f"„{QUERY}“ — 3 requests, sent together")
    print(f"  material:    {materials['returned']} of {materials['total']}")
    print(f"  collections: {collections['returned']} of at least "
          f"{collections['total']}")
    print()
    for hit in materials["hits"][:3]:
        print(f"  · {hit['title']}")
    print()
    for hit in collections["hits"][:3]:
        print(f"  ▣ {hit['title']}")
    return result


def show_filter_effect(repo: Repository) -> None:
    """A filter narrows the material only.

    The collection query takes a search word and nothing else. The flow says
    which filters it dropped rather than implying they applied to both.
    """
    filtered = repo.flows.search_all(QUERY, subject="Biologie", limit=5)
    print()
    print(f"with subject=Biologie: material {filtered['materials']['returned']}, "
          f"collections {filtered['collections']['returned']}")
    print(f"  not applied to the collections: "
          f"{filtered['collections']['filters_ignored']}")


def place_one(repo: Repository, hit: dict) -> dict | None:
    """Where one hit sits, or ``None`` when nothing about it is readable."""
    try:
        where = repo.flows.placement(hit["id"])
    except NotFoundError:
        print(f"\n{hit['title']}")
        print("  the index knows it, the repository does not")
        return None
    except PermissionDeniedError:
        # Only when BOTH halves are refused. One alone is reported in `failed`
        # below, and the other half still answers.
        print(f"\n{hit['title']}")
        print("  neither the way up nor the collections are readable")
        return None

    print(f"\n{where['title'] or hit['title']}")
    path = " > ".join(step["title"] for step in where["path"])
    print(f"  path:        {path or '(nothing readable above it)'}")
    print(f"  reaches:     {where['scope'] or '(not stated)'}")
    if where["collections"]:
        for coll in where["collections"]:
            print(f"  curated in:  {coll['title']}")
    else:
        print("  curated in:  no collection")
    # Measured on 2026-08-28: for material found by a search this is the norm,
    # not the exception -- /parents answers 500 AccessDeniedException for
    # foreign material, 18 of 20 hits. The collections half answered every
    # time, which is why the flow reports the refusal instead of raising.
    for part in where["failed"]:
        print(f"  not readable: {part['part']} ({part['reason'].split(':')[0]})")
    return where


def place_all(repo: Repository, result: dict) -> list[dict]:
    """What is one of these hits, actually?

    Both buckets on purpose. The search index holds nodes the repository no
    longer has -- measured on staging, 4 of 25 material hits -- and this is
    what that looks like from the outside.
    """
    print()
    print("-" * 62)
    hits = result["materials"]["hits"][:3] + result["collections"]["hits"][:3]
    # ``is not None``, not truthiness: ``place_one`` says "nothing readable"
    # with None, and an answer that happened to be empty is still an answer.
    return [w for hit in hits if (w := place_one(repo, hit)) is not None]


def compare_at_api_level(repo: Repository, placed: list[dict]) -> None:
    """The same two questions at the API level.

    A hit whose path half was refused is a fine flow answer and a bad subject
    for this comparison: ``node.parents()`` is the very call that was refused,
    and at the API level there is no ``failed`` to report it in -- it raises.
    Which is the trade the two levels make.
    """
    readable = next((p for p in placed if not p["failed"]), None)
    if readable is None:
        print("\nNo hit had a readable path — nothing to compare here.")
        return
    node = repo.node(readable["id"])
    print()
    print("-" * 62)
    print("API level, the same two questions as objects:")
    print(f"  node.parents()      -> {[f.title for f in node.parents()]}")
    print(f"  node.collections()  -> {[c.title for c in node.collections()]}")
    print()
    print("`parents` gives the nearest first, the way the endpoint answers;")
    print("`placement` turns it around, because a breadcrumb reads top down.")


def main() -> int:
    with Repository.from_env(metadataset="mds_oeh") as repo:
        result = search_both(repo)
        show_filter_effect(repo)
        placed = place_all(repo, result)
        if not placed:
            print("\nNothing was placeable — every hit refused both halves.")
            return 0
        compare_at_api_level(repo, placed)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
