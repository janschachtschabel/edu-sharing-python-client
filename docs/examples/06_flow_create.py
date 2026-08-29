"""Use case: create material with proper metadata.

    EDU_SHARING_USER=... EDU_SHARING_PASSWORD=... \
        python docs/examples/06_flow_create.py

Creates a throwaway folder of its own, works exclusively inside it, and removes
it afterwards. Nothing that was already there is touched.

What the flow takes off your hands:

* **Where does it go.** Omit ``parent_id`` and it lands in your home folder.
  At the API level that id sits four levels deep in the ``whoami()`` response.
* **Vocabulary while writing.** ``subject="Biologie"`` instead of
  ``ccm:taxonid=["http://w3id.org/openeduhub/vocabs/discipline/080"]``.
* **Saying what did not stick.** A value the metadata set does not know is
  reported rather than quietly dropped -- which matters here, because the
  material is created either way and looks complete.
"""

import json
import os
import sys
import uuid

from edusharing import EduSharingError, Node, Repository

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


def create_with_vocabulary(repo: Repository, folder: Node) -> dict:
    """Create material, giving labels instead of URIs."""
    created = repo.flows.add_material(
        "Photosynthesis explained simply",
        parent_id=folder.id,
        url="https://example.test/photosynthesis",
        description="A worked example from the library documentation",
        keywords=["Photosynthese", "Beispiel"],
        subject="Biologie",          # a label, resolved for you
        level="Sekundarstufe I",
    )
    print("Created:")
    print(json.dumps(created, ensure_ascii=False, indent=2))
    return created


def read_back(repo: Repository, node_id: str) -> None:
    """Read back from the server, not from the return value.

    The repository is the only place that says what actually stuck.
    """
    stored = repo.flows.describe(node_id)
    print("As the repository has it:")
    for field, values in stored["fields"].items():
        print(f"  {field}: {', '.join(values)}")
    print(f"  keywords: {', '.join(stored['keywords'])}")


def show_unknown_value(repo: Repository, folder: Node) -> None:
    """A value the metadata set does not know."""
    odd = repo.flows.add_material(
        "Material with an unknown subject",
        parent_id=folder.id,
        subject="Raumschiffbau",
    )
    print("With an unknown value:")
    for item in odd["unresolved"]:
        print(f"  ! {item['field']}={item['value']!r} was NOT written")
        if item["suggestions"]:
            print(f"    did you mean: {', '.join(item['suggestions'][:3])}?")
    print(f"  the material exists regardless: {odd['id']}")
    print()
    print("  This is the case worth knowing about: without the report,")
    print("  you would have material that looks tagged and is not.")


def main() -> int:
    with Repository(REPOSITORY, metadataset=METADATA_SET, auth=LOGIN) as repo:
        who = repo.whoami()
        if who.is_anonymous:
            print("Nothing can be written without signing in. Please set "
                  "EDU_SHARING_USER and EDU_SHARING_PASSWORD.", file=sys.stderr)
            return 1
        print(f"Signed in as {who.display_name}")
        print(f"Home folder: {who.home_folder}")
        print()

        folder = repo.create_node(
            who.home_folder,
            name=f"example-flows-{uuid.uuid4().hex[:8]}",
            type="cm:folder",
        )
        print(f"Throwaway folder created: {folder.name}")
        print()
        try:
            created = create_with_vocabulary(repo, folder)
            print()
            read_back(repo, created["id"])
            print()
            show_unknown_value(repo, folder)
        finally:
            folder.delete(recycle=False)
            print()
            print(f"Throwaway folder removed: {folder.name}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
