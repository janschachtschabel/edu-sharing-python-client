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

# The Windows console otherwise emits cp1252 and mangles umlauts.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from edusharing import (
    EduSharingError,
    NotFoundError,
    PermissionDeniedError,
    Repository,
)

QUERY = "Photosynthese"


def main() -> int:
    with Repository.from_env(metadataset="mds_oeh") as repo:
        # --- 1. Both buckets in one call --------------------------------
        result = repo.flows.search_all(QUERY, limit=5)
        materials = result["materials"]
        collections = result["collections"]

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

        # A filter narrows the material only — the collection query takes a
        # search word and nothing else. The flow says which filters it dropped
        # rather than implying they applied to both.
        filtered = repo.flows.search_all(QUERY, subject="Biologie", limit=5)
        print()
        print(f"with subject=Biologie: material {filtered['materials']['returned']}, "
              f"collections {filtered['collections']['returned']}")
        print(f"  not applied to the collections: "
              f"{filtered['collections']['filters_ignored']}")

        # --- 2. What is one of these hits, actually? --------------------
        # Both buckets on purpose. The search index holds nodes the repository
        # no longer has — measured on staging, 4 of 25 material hits — and this
        # is what that looks like from the outside.
        print()
        print("-" * 62)
        placed = []
        for hit in materials["hits"][:3] + collections["hits"][:3]:
            try:
                where = repo.flows.placement(hit["id"])
            except NotFoundError:
                print(f"\n{hit['title']}")
                print("  the index knows it, the repository does not")
                continue
            except PermissionDeniedError:
                print(f"\n{hit['title']}")
                print("  readable, but the way up is not")
                continue
            placed.append(where)

            print(f"\n{where['title']}")
            path = " > ".join(step["title"] for step in where["path"])
            print(f"  path:        {path or '(nothing readable above it)'}")
            print(f"  reaches:     {where['scope'] or '(not stated)'}")
            if where["collections"]:
                for coll in where["collections"]:
                    print(f"  curated in:  {coll['title']}")
            else:
                print("  curated in:  no collection")

        if not placed:
            print("\nNothing was placeable — unusual, and not an error here.")
            return 0

        # --- 3. The same two questions at the API level -----------------
        node = repo.node(placed[0]["id"])
        print()
        print("-" * 62)
        print("API level, the same two questions as objects:")
        print(f"  node.parents()      -> {[f.title for f in node.parents()]}")
        print(f"  node.collections()  -> {[c.title for c in node.collections()]}")
        print()
        print("`parents` gives the nearest first, the way the endpoint answers;")
        print("`placement` turns it around, because a breadcrumb reads top down.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
