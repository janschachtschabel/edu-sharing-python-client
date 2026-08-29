"""Use case: make material visible to others -- the step nothing does for you.

    EDU_SHARING_USER=... EDU_SHARING_PASSWORD=... python docs/examples/11_publish.py

Creates a throwaway folder of its own, works exclusively inside it, and removes
it afterwards. Nothing that was already there is touched.

What is demonstrated: material an application creates is readable by its
creator and by **nobody else**, and neither filing it into a collection nor
`scope="PUBLIC"` on that collection changes it. Every call along the way
answers 200.
"""

import os
import sys
import uuid

from edusharing import ConflictError, EduSharingError, Identity, Node, Repository

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


def create_invisible(repo: Repository, folder: Node) -> Node:
    """Created, and invisible to everyone else."""
    node = repo.create_node(folder.id, name="material.txt", title="Photosynthese")
    print(f"created: {node.url}")
    print(f"  public: {node.is_public}   <- free, the response carries it")
    return node


def file_into_public_collection(repo: Repository, node: Node) -> Node:
    """Into a public collection -- and still invisible.

    This is the finding the Ideendatenbank hit in production.
    """
    collection = repo.create_collection(
        f"Beispiel {uuid.uuid4().hex[:6]}", scope="PUBLIC")
    repo.add_to_collection(collection.id, node.id)
    print()
    print(f"filed into a scope=PUBLIC collection: {collection.id}")
    print(f"  collection public: {repo.node(collection.id).is_public}")
    print(f"  material public:   {repo.node(node.id).is_public}")
    print("  (the scope says where a collection is listed, not who may open it)")
    return collection


def publish_and_take_back(repo: Repository, node: Node, who: Identity) -> None:
    """The step that actually does it -- and what survives it.

    The repository's own POST replaces the whole local list, so publishing
    without merging would take away everyone else's rights, with a 200 in
    front.
    """
    print()
    print(f"publish():  {node.permissions.publish()}   <- changed now")
    print(f"publish():  {node.permissions.publish()}   <- already was")
    print(f"  public: {repo.node(node.id).is_public}")

    node.permissions.grant(who.authority, "Coordinator")
    rights = node.permissions.get()
    print()
    print(f"  own entries: {[a.authority for a in rights.own]}")
    print(f"  still public after granting: {rights.is_public}")

    print()
    print(f"unpublish(): {node.permissions.unpublish()}")
    print(f"  public: {repo.node(node.id).is_public}")


def show_inheritance(repo: Repository, node: Node, folder: Node) -> None:
    """A node is public when its folder is -- without an entry of its own.

    Withdrawing locally would change nothing, so ``unpublish`` says so instead
    of reporting a success that did not happen.
    """
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


def publish_at_flow_level(repo: Repository, folder: Node) -> None:
    """The same question at the flow level, in one call."""
    print()
    result = repo.flows.add_material(
        "Direkt veröffentlicht", parent_id=folder.id, publish=True)
    print(f"flows.add_material(publish=True) -> public: {result['public']}")


def main() -> int:
    with Repository(REPOSITORY, metadataset=METADATA_SET, auth=LOGIN) as repo:
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
            node = create_invisible(repo, folder)
            collection = file_into_public_collection(repo, node)
            publish_and_take_back(repo, node, who)
            show_inheritance(repo, node, folder)
            publish_at_flow_level(repo, folder)
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
