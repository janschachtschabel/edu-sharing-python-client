"""Use case: build a collection, fill it, take it down again.

    EDU_SHARING_USER=... EDU_SHARING_PASSWORD=... \\
        python docs/examples/07_flow_collection.py

Creates its own throwaway folder and its own throwaway collection, and removes
both afterwards. Nothing that was already there is touched.

Two things this shows that are easy to get wrong by hand:

* **Partial success is the normal case.** Placing material into a collection is
  one call per node, and each can fail on its own. ``build_collection`` reports
  ``added`` and ``failed`` separately instead of raising on the first problem
  and leaving a half-filled collection behind.
* **Deleting says what went.** ``delete`` reads the node first, so the answer
  names what is now gone. A bare "done" leaves you unsure whether you hit the
  right thing -- and a language model then confirms something to a person
  without knowing what.
"""

import json
import sys
import uuid

# The Windows console otherwise emits cp1252 and mangles umlauts.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from edusharing import Repository


def main() -> int:
    with Repository.from_env(metadataset="mds_oeh") as repo:
        who = repo.whoami()
        if who.is_anonymous:
            print("Nothing can be written without signing in. Please set "
                  "EDU_SHARING_USER and EDU_SHARING_PASSWORD.", file=sys.stderr)
            return 1

        folder = repo.create_node(
            who.home_folder,
            name=f"example-coll-{uuid.uuid4().hex[:8]}",
            type="cm:folder",
        )
        collection_id = None

        try:
            # --- 1. Two pieces of material to collect ---------------------
            first = repo.flows.add_material(
                "Collection example: leaf anatomy",
                parent_id=folder.id, subject="Biologie")
            second = repo.flows.add_material(
                "Collection example: light reactions",
                parent_id=folder.id, subject="Biologie")
            print(f"Two pieces of material created: {first['id']}, {second['id']}")
            print()

            # --- 2. Collection, created and filled in one call ------------
            # A deliberately broken id goes in as well, to show what a partial
            # success looks like.
            collection = repo.flows.build_collection(
                f"Example collection {uuid.uuid4().hex[:6]}",
                description="Created by the library documentation",
                node_ids=[first["id"], "definitely-not-a-node-id", second["id"]],
            )
            collection_id = collection["id"]

            print("Collection:")
            print(json.dumps(collection, ensure_ascii=False, indent=2)[:600])
            print()
            print(f"  placed:  {len(collection['added'])}")
            print(f"  failed:  {len(collection['failed'])}")
            for failure in collection["failed"]:
                print(f"    {failure['id']}: {failure['reason'][:80]}")
            print()
            print("  The collection exists regardless. Aborting on the first")
            print("  failure would have left one nobody asked for.")

        finally:
            # --- 3. Take it down, and let it say what went ----------------
            if collection_id:
                removed = repo.flows.delete(collection_id, recycle=False)
                print()
                print(f"Deleted: {removed['title']!r} ({removed['type']}), "
                      f"permanently={not removed['recycled']}")
            folder.delete(recycle=False)
            print(f"Throwaway folder removed: {folder.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
