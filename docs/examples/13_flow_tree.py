"""Use case: walk a collection, search inside it, count what is in it.

    python docs/examples/13_flow_tree.py

Reads only. Nothing is created, changed or deleted, so this runs anonymously —
sign in and you simply see more.

The three flows share one problem, and it is not a technical one: collections
form a *graph*, not a tree, and a search cannot be scoped to one. Both are
measured, both are why these flows walk and compare locally, and both are why
every answer says what it left out.
"""

import os
import sys

from edusharing import EduSharingError, Repository

# The Windows console otherwise emits cp1252 and mangles umlauts.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- Configuration ---------------------------------------------------
# Point these at your own repository. The values below are the staging
# instance, filled in so this example runs as it stands; anything set in the
# environment wins over them. Configured once, here -- no call below takes an
# address of its own.
REPOSITORY = os.environ.get(
    "EDU_SHARING_URL", "https://repository.staging.openeduhub.net")
METADATA_SET = os.environ.get("EDU_SHARING_MDS", "mds_oeh")

# Left empty on purpose: without them the example runs anonymously, which is
# enough for reading. Writing needs both -- fill them in, or set
# EDU_SHARING_USER and EDU_SHARING_PASSWORD in the environment.
USER = os.environ.get("EDU_SHARING_USER", "")
PASSWORD = os.environ.get("EDU_SHARING_PASSWORD", "")
LOGIN = (USER, PASSWORD) if USER else None

TOPIC = "Biologie"
TERM = "zelle"


def print_tree(collections: list[dict], indent: int = 1) -> None:
    for entry in collections:
        print(f"{'  ' * indent}{entry['title']}")
        print_tree(entry["collections"], indent + 1)


def show_tree(repo: Repository, collection: dict) -> None:
    """What is underneath it -- and whether the walk saw all of it."""
    tree = repo.flows.browse_tree(collection["id"], depth=2, max_collections=12)
    print(f"\nTree, {tree['opened']} collections opened"
          f"{', cut short' if tree['truncated'] else ''}:")
    print_tree(tree["collections"])
    if not tree["collections"]:
        print("  (none underneath)")


def show_stats(repo: Repository, collection: dict) -> None:
    """How much is in it. The counts are exact, the breakdown is a sample."""
    stats = repo.flows.collection_stats(collection["id"], sample=50)
    print(f"\n{stats['materials']} materials, "
          f"{stats['collections']} sub-collections")
    print(f"  tallied over {stats['sampled']}"
          f"{' — all of them' if stats['complete'] else ' of them, a sample'}")
    for field, counter in sorted(stats["by"].items()):
        top = sorted(counter.items(), key=lambda kv: -kv[1])[:3]
        if top:
            print(f"  {field:10s} {', '.join(f'{k} ({v})' for k, v in top)}")


def search_inside(repo: Repository, collection: dict) -> None:
    """Find something inside it -- by walking, because scoping is impossible."""
    hits = repo.flows.search_in_collection(
        collection["id"], TERM, depth=2, max_collections=12)
    print(f"\n{TERM!r} in {hits['searched']} collections: "
          f"{len(hits['hits'])} hits"
          f"{', cut short' if hits['truncated'] else ''}")
    for hit in hits["hits"][:5]:
        print(f"  · {hit['title']}")
    if not hits["hits"]:
        print("  (nothing — and 'truncated' above says whether that is"
              " the whole answer)")


def show_related(repo: Repository, materials: list[dict]) -> None:
    """More like one of them -- a resemblance, not an asserted relation."""
    for material in materials:
        try:
            like = repo.flows.related(material["id"], limit=3)
        except EduSharingError as exc:
            print(f"\n{material['title']}\n  not usable: {type(exc).__name__}")
            continue
        print(f"\nMore like {like['seed']['title']!r}")
        print(f"  based on: {like['based_on'] or '(nothing to go on)'}")
        for hit in like["hits"]:
            print(f"  · {hit['title']}")
        if like["reason"]:
            print(f"  {like['reason']}")
        return


def describe_all_at_once(repo: Repository, materials: list[dict]) -> None:
    """And all of them in one call, one deliberately dead id among them."""
    ids = [m["id"] for m in materials]
    many = repo.flows.describe_many([*ids, "gibtesnicht-0000"])
    print()
    print("-" * 62)
    print(f"describe_many: {many['found']} of {many['requested']} loaded")
    for gone in many["failed"]:
        print(f"  gone: {gone['id']}  ({gone['reason'].split(':')[0]})")
    print("  A dead index entry is reported, not raised — measured, 4 of 25")
    print("  search hits were no longer retrievable.")


def main() -> int:
    with Repository(REPOSITORY, metadataset=METADATA_SET, auth=LOGIN) as repo:
        found = repo.flows.find_collections(TOPIC, limit=3)
        if not found["hits"]:
            print(f"No collection for {TOPIC!r}.", file=sys.stderr)
            return 0

        collection = found["hits"][0]
        print(f"Collection: {collection['title']}  ({collection['id']})")
        print("-" * 62)

        show_tree(repo, collection)
        show_stats(repo, collection)
        search_inside(repo, collection)

        contents = repo.flows.collection_contents(collection["id"], limit=5)
        show_related(repo, contents["materials"])
        describe_all_at_once(repo, contents["materials"])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
