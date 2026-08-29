"""Use case: find a collection, open it, change what is inside.

    EDU_SHARING_USER=... EDU_SHARING_PASSWORD=... \\
        python docs/examples/09_flow_browse.py

Reading is anonymous; the last section needs credentials and creates a
throwaway folder of its own, which it removes afterwards. Nothing that was
already there is touched.

This is the chain an MCP server runs most often: search collections, look
inside one, and act on what is there.
"""

import os
import sys
import uuid

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


def find_collections(repo: Repository) -> list[dict]:
    """Search collections, and say why the number is a floor."""
    found = repo.flows.find_collections("Physik", limit=5)
    print(f"{found['total']} collections found "
          f"(a lower bound: {found['total_is_lower_bound']} -- two routes merged)")
    for hit in found["hits"][:5]:
        print(f"  {hit['title']}")
    return found["hits"]


def show_contents(repo: Repository, collection: dict) -> None:
    """Open one collection and look at what is inside."""
    contents = repo.flows.collection_contents(collection["id"], limit=5)
    print(f"Inside {collection['title']!r}:")
    print(f"  {contents['total_materials']} materials, "
          f"showing {contents['returned_materials']}")
    for material in contents["materials"][:3]:
        fields = ", ".join(
            f"{k}={'/'.join(v)}" for k, v in list(material["fields"].items())[:2])
        print(f"    {material['title'][:52]}")
        if fields:
            print(f"      {fields}")
    if contents["collections"]:
        print(f"  {len(contents['collections'])} sub-collections:")
        for sub in contents["collections"][:3]:
            print(f"    {sub['title']}")
    else:
        # Worth stating: asking only for material would show the same emptiness
        # even when sub-collections exist.
        print("  no sub-collections")


def edit(repo: Repository) -> None:
    """Create, change, verify, remove. Needs credentials."""
    who = repo.whoami()
    folder = repo.create_node(
        who.home_folder,
        name=f"example-browse-{uuid.uuid4().hex[:8]}",
        type="cm:folder",
    )
    try:
        created = repo.flows.add_material(
            "Browse example: optics", parent_id=folder.id, subject="Physik")
        print(f"  created {created['id']}")

        changed = repo.flows.update_material(
            created["id"],
            title="Browse example: optics, revised",
            keywords=["Optik", "überarbeitet"],
            subject="Biologie",          # a label, resolved on write too
        )
        print(f"  changed to {changed['title']!r}, "
              f"unresolved: {changed['unresolved'] or 'none'}")

        # Verify at the server, not from the return value.
        state = repo.flows.describe(created["id"])
        print(f"  as stored: subject={state['fields'].get('subject')}, "
              f"keywords={state['keywords']}")
    finally:
        folder.delete(recycle=False)
        print(f"  throwaway folder removed: {folder.name}")


def main() -> int:
    with Repository(REPOSITORY, metadataset=METADATA_SET, auth=LOGIN) as repo:
        print("Browsing collections")
        print("=" * 72)
        hits = find_collections(repo)
        if hits:
            print()
            show_contents(repo, hits[0])

        print()
        print("Changing material")
        print("=" * 72)
        who = repo.whoami()
        if who.is_anonymous:
            print("  skipped -- set EDU_SHARING_USER and EDU_SHARING_PASSWORD "
                  "to run this part.")
            return 0
        edit(repo)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
