"""Use case: what does this collection's curated page actually show?

    python docs/examples/14_flow_page.py

Reads only. Nothing is created, changed or deleted, so this runs anonymously —
sign in and you simply see more.

edu-sharing's page builder lets a collection carry a landing page: swimlanes,
widgets, and the nodes those widgets point at. WirLernenOnline calls these
"Themenseiten", but the properties belong to edu-sharing, so this example
speaks of pages.

Two things it deliberately shows rather than hides:

* a collection can carry a page that renders **nothing** — a variant with zero
  swimlanes is a real, measured state;
* a widget holding a saved search is **reported, not run**. Its filters carry
  `virtual:` fields the metadata set does not know, and guessing at them would
  produce a result nobody asked for.
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

TOPIC = "Deutsch"


def print_item(item: dict) -> None:
    print(f"    {item['widget']}"
          f"{'' if item['node_id'] else '   (no node — it needs none)'}")
    if item.get("description"):
        print(f"      “{item['description'][:70].strip()}…”")
    if "node_ids" in item:
        print(f"      fixed list: {len(item['node_ids'])} nodes")
    if "search" in item:
        text = item["search"]["text"] or "(no term)"
        print(f"      saved search: {text!r}, "
              f"{len(item['search']['filters'])} filters — NOT run")
    for problem in ("unreadable", "unreachable"):
        if problem in item:
            print(f"      {problem}: {item[problem]}")


def find_pages(repo: Repository) -> dict:
    """Which collections carry a page at all."""
    found = repo.flows.find_pages(TOPIC, limit=25)
    at_least = "at least " if found["total_is_lower_bound"] else ""
    print(f"{len(found['hits'])} of {found['checked']} judgeable hits carry "
          f"a page (the search matched {at_least}{found['total']} collections)")
    if found["reason"]:
        print(f"  note: {found['reason']}")
    for hit in found["hits"]:
        print(f"  · {hit['title']}  ({hit['id']})")
    return found


def show_variants(page: dict) -> None:
    """Which variant renders, and why that one."""
    print()
    print("=" * 66)
    print(f"{page['collection']['title']}   (folder {page['folder_id']})")

    rendered = page["rendered"]
    chosen = "no variant is recorded — the first of the list renders" \
        if rendered["by_position"] else "recorded in the page document"
    print(f"renders: {rendered['title']!r} — {chosen}")

    for variant in page["variants"]:
        mark = "*" if variant["id"] == rendered["id"] else " "
        extra = [k for k in ("intention",) if variant[k]]
        print(f" {mark} {variant['title'][:38]:40s}"
              f" template={variant['is_template']}"
              f" readable={variant['readable']}"
              f"{' ' + variant['intention'] if extra else ''}")


def show_swimlanes(page: dict) -> None:
    """The page itself -- which may be empty, and that is a real state."""
    if not page["swimlanes"]:
        print("\nThis page renders nothing: its variant configures zero"
              "\nswimlanes. Having a page and having content are two"
              "\nquestions, and this is the measured answer to the second.")
        return

    print(f"\n{len(page['swimlanes'])} swimlanes"
          f"{', cut short' if page['truncated'] else ''}:")
    for lane in page["swimlanes"]:
        print(f"\n  {lane['heading'] or '(no heading)'}   [{lane['type']}]")
        for item in lane["items"]:
            print_item(item)
    print(f"\n{len(page['node_ids'])} nodes embedded across the page.")


def compare_at_api_level(repo: Repository, page: dict) -> None:
    """The same page at the API level.

    The flow answers with a dict, ready to hand on. The API level answers with
    objects you keep working with -- and it is where writing lives.
    """
    node = repo.node(page["collection"]["id"])
    curated = node.page.get()               # None for a node without one
    print()
    print("-" * 66)
    print("API level, the same page as objects:")
    print(f"  node.page.get()      -> {curated!r}")
    print(f"  .by_position         -> {curated.by_position}")
    print(f"  .rendered.swimlanes  -> {len(curated.rendered.swimlanes)}")
    print(f"  .rendered.node_ids   -> {len(curated.rendered.node_ids)} nodes")
    for variant in curated.variants:
        mark = "renders" if variant.id == curated.rendered.id else "       "
        print(f"  {mark}  {variant.id[:8]}…  {variant.title!r}")

    print()
    print("Writing goes the same way and is NOT done here:")
    print("    node.page.render(variant_id)      # immediately public")
    print("It edits the stored document rather than composing one, refuses")
    print("what it cannot prove, and reads back. This example only reads --")
    print("and the test account may not write a page it did not build.")


def main() -> int:
    with Repository(REPOSITORY, metadataset=METADATA_SET, auth=LOGIN) as repo:
        found = find_pages(repo)
        if not found["hits"]:
            print("\nNo curated page under this term. That is not a fault — the"
                  "\npage builder is one of edu-sharing's options, not a duty."
                  "\nAnd one run is a sample: measured, the same call answered"
                  "\nwith three different hit sets in a row.", file=sys.stderr)
            return 0

        page = repo.flows.page(found["hits"][0]["id"], resolve_widgets=True,
                               max_widgets=8)
        show_variants(page)
        show_swimlanes(page)
        compare_at_api_level(repo, page)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
