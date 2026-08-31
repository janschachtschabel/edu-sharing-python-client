"""Use case: open a collection and see what is in it, and what is missing.

    python docs/examples/19_collection_audit.py

Reads only. Runs anonymously -- and the last section shows why signing in is
not automatically the answer.

The editorial question, in one run: how big is this collection, what is it
made of, and which materials lack the metadata that makes them findable.

**The point of the example is the last section.** Written the obvious way,
this script printed "sits nowhere" for a material that demonstrably sat in the
collection it had just been read from. The library was right and the script was
wrong: ``placement`` asks two questions at once, either half can be refused on
its own, and it says which in ``failed``. Anonymously, the way up answers
``500 AccessDeniedException`` while the collections come back fine.

An empty ``path`` therefore means one of two very different things, and only
``failed`` tells them apart:

* nothing refused -> the node really does hang directly in a home folder;
* ``part: "path"`` in ``failed`` -> you were not allowed to see where it sits.

Signing in does **not** necessarily lift it -- measured 2026-08-31, the same
refusal came back with credentials, because a collection holds a *reference*
and the original hangs in a folder this account cannot read either. Which is
the whole point: the refusal is a fact about the answer, not a hint to try
harder.

The same shape appears in ``browse_tree`` (``truncated``) and in
``search_in_collection`` (``unreadable``). Reading the result without them is
how a partial answer passes for a complete one.
"""

import asyncio
import os
import sys

from edusharing import AsyncRepository, EduSharingError

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

# Left empty on purpose: reading works anonymously. Credentials widen what the
# account may see -- but not always, as the last section measures.
USER = os.environ.get("EDU_SHARING_USER", "")
PASSWORD = os.environ.get("EDU_SHARING_PASSWORD", "")
LOGIN = (USER, PASSWORD) if USER else None

TOPIC = "Biologie"
#: The fields a material needs to be findable by a filtered search.
REQUIRED = ("subject", "level", "type")


def print_shape(tree: dict, stats: dict) -> None:
    """How big it is -- and whether the figures are the whole story."""
    print(f"  tree:     {tree['opened']} collections opened"
          f"{', CUT SHORT' if tree['truncated'] else ''}")
    print(f"  contents: {stats['materials']} materials, "
          f"{stats['collections']} sub-collections")
    print(f"            tallied over {stats['sampled']}"
          f"{' — all of them' if stats['complete'] else ' — a sample'}")
    for field, counter in sorted(stats["by"].items()):
        top = sorted(counter.items(), key=lambda kv: -kv[1])[:3]
        if top:
            print(f"            {field:<10} "
                  f"{', '.join(f'{k} ({v})' for k, v in top)}")


def print_gaps(many: dict) -> None:
    """Which materials are missing what a filtered search needs."""
    print()
    print(f"  {many['found']} of {many['requested']} materials loaded")
    for gone in many["failed"]:
        print(f"    no longer there: {gone['id']}  ({gone['reason'].split(':')[0]})")

    gaps = dict.fromkeys(REQUIRED, 0)
    without_description = 0
    for node in many["nodes"]:
        for field in REQUIRED:
            if not node["fields"].get(field):
                gaps[field] += 1
        if not (node["description"] or "").strip():
            without_description += 1

    print(f"  gaps across {many['found']} materials:")
    for field, count in gaps.items():
        print(f"    {field:<12} missing on {count}")
    print(f"    {'description':<12} missing on {without_description}")


def print_placement(where: dict) -> None:
    """Where one material sits -- and whether that answer is complete.

    ``failed`` first. Printing ``path`` without it is exactly the mistake this
    example exists to show.
    """
    print()
    if where["failed"]:
        for part in where["failed"]:
            print(f"  {part['part']} REFUSED: {part['reason'].split(':')[0]}"
                  f" — this is not 'there is none'")
        print("  (measured 2026-08-31: signing in does NOT lift this one —"
              " the material is a reference whose original lives elsewhere)")
    print(f"  path:        {' / '.join(where['path']) or '(none returned)'}")
    print(f"  collections: {len(where['collections'])}")


async def main() -> int:
    async with AsyncRepository(
            REPOSITORY, metadataset=METADATA_SET, auth=LOGIN) as repo:
        found = await repo.flows.find_collections(TOPIC, limit=3)
        print(f"{found['total']} collections for {TOPIC!r}"
              f"{' (a lower bound)' if found['total_is_lower_bound'] else ''}")
        if not found["hits"]:
            print("none — nothing to audit")
            return 0

        collection = found["hits"][0]
        print(f"audited: {collection['title']}  ({collection['id']})")
        print()

        tree, stats = await asyncio.gather(
            repo.flows.browse_tree(collection["id"], depth=2),
            repo.flows.collection_stats(collection["id"], sample=40),
        )
        print_shape(tree, stats)

        inside = await repo.flows.collection_contents(collection["id"], limit=25)
        ids = [m["id"] for m in inside["materials"]]
        if not ids:
            print("  empty — no materials to check")
            return 0

        many = await repo.flows.describe_many(ids)
        print_gaps(many)
        print_placement(await repo.flows.placement(many["nodes"][0]["id"]))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
