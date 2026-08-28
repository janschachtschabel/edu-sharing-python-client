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

import sys

# The Windows console otherwise emits cp1252 and mangles umlauts.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from edusharing import EduSharingError, Repository

TOPIC = "Deutsch"


def main() -> int:
    with Repository.from_env(metadataset="mds_oeh") as repo:
        # --- 1. Which collections carry a page at all -------------------
        found = repo.flows.find_pages(TOPIC, limit=25)
        at_least = "at least " if found["total_is_lower_bound"] else ""
        print(f"{len(found['hits'])} of {found['checked']} judgeable hits carry "
              f"a page (the search matched {at_least}{found['total']} collections)")
        if found["reason"]:
            print(f"  note: {found['reason']}")
        for hit in found["hits"]:
            print(f"  · {hit['title']}  ({hit['id']})")

        if not found["hits"]:
            print("\nNo curated page under this term. That is not a fault — the"
                  "\npage builder is one of edu-sharing's options, not a duty."
                  "\nAnd one run is a sample: measured, the same call answered"
                  "\nwith three different hit sets in a row.", file=sys.stderr)
            return 0

        # --- 2. What the first one renders ------------------------------
        page = repo.flows.page(found["hits"][0]["id"], resolve_widgets=True,
                               max_widgets=8)
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

        # --- 3. The page itself -----------------------------------------
        if not page["swimlanes"]:
            print("\nThis page renders nothing: its variant configures zero"
                  "\nswimlanes. Having a page and having content are two"
                  "\nquestions, and this is the measured answer to the second.")
        else:
            print(f"\n{len(page['swimlanes'])} swimlanes"
                  f"{', cut short' if page['truncated'] else ''}:")
            for lane in page["swimlanes"]:
                print(f"\n  {lane['heading'] or '(no heading)'}   [{lane['type']}]")
                for item in lane["items"]:
                    _print_item(item)

            print(f"\n{len(page['node_ids'])} nodes embedded across the page.")

        # --- 4. The same page at the API level ---------------------------
        # The flow answers with a dict, ready to hand on. The API level answers
        # with objects you keep working with -- and it is where writing lives.
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
            print(f"  {mark}  {variant.id[:8]}\u2026  {variant.title!r}")

        print()
        print("Writing goes the same way and is NOT done here:")
        print("    node.page.render(variant_id)      # immediately public")
        print("It edits the stored document rather than composing one, refuses")
        print("what it cannot prove, and reads back. This example only reads --")
        print("and the test account may not write a page it did not build.")

    return 0


def _print_item(item: dict) -> None:
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


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
