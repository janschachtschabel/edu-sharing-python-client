"""Use case: what belongs to a material, and what stands beside it.

    EDU_SHARING_USER=... EDU_SHARING_PASSWORD=... \
        python docs/examples/17_flow_belonging.py

Creates its own throwaway folder with three materials in it and removes all of
it afterwards. Nothing that was already there is touched.

edu-sharing has three different kinds of belonging, and mixing them up is the
usual mistake:

* **A collection** holds references to material that also lives elsewhere.
  ``collection_contents`` reads it -- see ``07_flow_collection.py``.
* **A child object** hangs *under* one material: an answer sheet, a handout, a
  second file format. It has no life of its own. ``child_objects`` reads them.
* **A relation** joins two materials that stand *side by side*: a series and
  its episodes, a worksheet and the video it is based on. Both remain full
  materials. ``relations`` reads them.

Two traps this shows, both measured:

* A child object carries its filename in ``name`` and an **empty** ``title``.
  Every other flow displays ``title``, so reaching for it here shows nothing.
* ``relations.create(metadata=...)`` is accepted with HTTP 200 and stored
  nowhere. The library reads back and raises ``SilentDropError`` rather than
  reporting a success that did not happen.
"""

import os
import sys
import uuid

from edusharing import EduSharingError, Node, Repository, SilentDropError

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

# Writing needs a login -- there is nothing to create anonymously. Fill these
# in, or set EDU_SHARING_USER and EDU_SHARING_PASSWORD in the environment.
USER = os.environ.get("EDU_SHARING_USER", "")
PASSWORD = os.environ.get("EDU_SHARING_PASSWORD", "")
LOGIN = (USER, PASSWORD) if USER else None

ANSWER_SHEET = b"1/2 + 1/4 = 3/4\n"


def make_materials(repo: Repository, folder: Node) -> dict[str, str]:
    """One series and two episodes, all in the throwaway folder."""
    made = {}
    for key, title in [("series", "Bruchrechnen (Reihe)"),
                       ("part1", "Bruchrechnen, Folge 1"),
                       ("part2", "Bruchrechnen, Folge 2")]:
        answer = repo.flows.add_material(
            title, parent_id=folder.id, url=f"https://example.org/{key}")
        made[key] = answer["id"]
        print(f"  {title!r} -> {answer['id']}")
    return made


def attach_child(repo: Repository, node_id: str) -> None:
    """Hang an answer sheet under one episode, then read it back."""
    node = repo.node(node_id)
    node.children.add(ANSWER_SHEET, filename="loesung.txt",
                      mimetype="text/plain", order=0)

    answer = repo.flows.child_objects(node_id)
    print(f"\nchild_objects: {answer['count']} attached")
    for child in answer["children"]:
        # name, not title -- the title of a child object is empty.
        print(f"  · {child['name']}  ({child['mimetype']}, "
              f"position {child['order']}, {len(child['title'])} chars of title)")


def link_side_by_side(repo: Repository, made: dict[str, str]) -> None:
    """Join the episodes to the series, then read the series' own view."""
    for part in ("part1", "part2"):
        repo.relations.create(made[part], "isPartOf", made["series"])

    # The opposite direction is kept by the repository, so asking the series
    # reports hasPart -- for a link that was created the other way round.
    answer = repo.flows.relations(made["series"])
    print(f"\nrelations of the series: {answer['count']}")
    for link in answer["relations"]:
        flags = "machine-proposed" if link["ai_generated"] else "by a person"
        print(f"  · {link['type']:8s} {link['title']!r}  "
              f"({flags}, approved={link['approved']})")

    # And the same link seen from an episode -- the other name for it.
    from_part = repo.flows.relations(made["part1"])
    print(f"  the episode calls it: {from_part['relations'][0]['type']!r}")


def show_the_dropped_argument(repo: Repository, made: dict[str, str]) -> None:
    """metadata= is accepted and stored nowhere. The library says so."""
    try:
        repo.relations.create(
            made["part2"], "references", made["part1"],
            metadata={"reason": "model, confidence 0.88"})
    except SilentDropError as exc:
        print(f"\nSilentDropError, as it should be: {exc}")
        print("  The link itself was made -- only the reasoning was dropped.")
        print("  Keep it on the nodes, or in your own store.")
    else:
        print("\nmetadata= survived. This instance behaves differently from")
        print("  edu-sharing 11.0, where it was measured to be dropped.")


def take_down(repo: Repository, folder: Node) -> None:
    """Everything this example made, and nothing else."""
    folder.delete(recycle=False)
    print(f"\nThrowaway folder removed: {folder.name}")


def main() -> int:
    with Repository(REPOSITORY, metadataset=METADATA_SET, auth=LOGIN) as repo:
        who = repo.whoami()
        if who.is_anonymous:
            print("Nothing can be written without signing in. Please set "
                  "EDU_SHARING_USER and EDU_SHARING_PASSWORD.", file=sys.stderr)
            return 1

        folder = repo.create_node(
            who.home_folder,
            name=f"example-belonging-{uuid.uuid4().hex[:8]}",
            type="cm:folder",
        )
        print(f"Throwaway folder: {folder.name}")
        try:
            made = make_materials(repo, folder)
            attach_child(repo, made["part1"])
            link_side_by_side(repo, made)
            show_the_dropped_argument(repo, made)
        finally:
            take_down(repo, folder)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
