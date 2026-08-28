"""Use case: make material visible to others -- the step nothing does for you.

    EDU_SHARING_USER=... EDU_SHARING_PASSWORD=... python docs/examples/11_publish.py

Creates a throwaway folder of its own, works exclusively inside it, and removes
it afterwards. Nothing that was already there is touched.

What is demonstrated: material an application creates is readable by its
creator and by **nobody else**, and neither filing it into a collection nor
`scope="PUBLIC"` on that collection changes it. Every call along the way
answers 200.
"""

import sys
import uuid

# The Windows console otherwise emits cp1252 and mangles umlauts.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from edusharing import ConflictError, EduSharingError, Repository


def main() -> int:
    with Repository.from_env(metadataset="mds_oeh") as repo:
        who = repo.whoami()
        if who.is_anonymous:
            print("Nothing can be published without signing in. Please set "
                  "EDU_SHARING_USER and EDU_SHARING_PASSWORD.", file=sys.stderr)
            return 1
        print(f"Signed in as {who.display_name} ({who.authority})")
        print()

        folder = repo.create_node(
            who.home_folder, name=f"example-{uuid.uuid4().hex[:8]}", type="cm:folder")
        collection = None
        try:
            # 1. Created, and invisible to everyone else.
            node = repo.create_node(folder.id, name="material.txt",
                                    title="Photosynthese")
            print(f"created: {node.url}")
            print(f"  public: {node.is_public}   <- free, the response carries it")

            # 2. Into a public collection -- and still invisible. This is the
            #    finding the Ideendatenbank hit in production.
            collection = repo.create_collection(
                f"Beispiel {uuid.uuid4().hex[:6]}", scope="PUBLIC")
            repo.add_to_collection(collection.id, node.id)
            print()
            print(f"filed into a scope=PUBLIC collection: {collection.id}")
            print(f"  collection public: {repo.node(collection.id).is_public}")
            print(f"  material public:   {repo.node(node.id).is_public}")
            print("  (the scope says where a collection is listed, not who may"
                  " open it)")

            # 3. The step that actually does it.
            print()
            print(f"publish():  {node.permissions.publish()}   <- changed now")
            print(f"publish():  {node.permissions.publish()}   <- already was")
            print(f"  public: {repo.node(node.id).is_public}")

            # 4. Other permissions survive it. The repository's own POST
            #    replaces the whole local list -- publishing without merging
            #    would take away everyone else's rights, with a 200 in front.
            node.permissions.grant(who.authority, "Coordinator")
            rights = node.permissions.get()
            print()
            print(f"  own entries: {[a.authority for a in rights.own]}")
            print(f"  still public after granting: {rights.is_public}")

            # 5. And back.
            print()
            print(f"unpublish(): {node.permissions.unpublish()}")
            print(f"  public: {repo.node(node.id).is_public}")

            # 6. A node is public when its folder is -- without an entry of its
            #    own. Withdrawing locally would change nothing, so it says so.
            folder.permissions.publish()
            inherited = repo.node(node.id)
            print()
            print(f"folder published -> material public again: {inherited.is_public}")
            print(f"  own entry for everyone: "
                  f"{node.permissions.get().find('GROUP_EVERYONE') is not None}")
            try:
                node.permissions.unpublish()
                print("  ! no error -- that would be surprising.")
            except ConflictError as clash:
                print(f"  unpublish() refuses: {str(clash)[:90]}…")

            # 7. The same question at the flow level, in one call.
            print()
            result = repo.flows.add_material(
                "Direkt veröffentlicht", parent_id=folder.id, publish=True)
            print(f"flows.add_material(publish=True) -> public: {result['public']}")

        finally:
            if collection is not None:
                collection.delete()
            folder.delete()
            print()
            print("Throwaway folder removed -- the holdings are as they were found.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
