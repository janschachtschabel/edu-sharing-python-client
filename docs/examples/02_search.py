"""Searching with labels instead of URIs -- without presupposing the instance.

    python docs/examples/02_search.py
    python docs/examples/02_search.py Photosynthese

Shows the point of this library: the same three lines run against any metadata
set, because filter values are resolved at runtime against *this* instance.
"""

import sys

from edusharing import EduSharingError, Repository

# The Windows console otherwise emits cp1252 and mangles umlauts.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT = "https://repository.staging.openeduhub.net"


def main(topic: str = "Photosynthese") -> int:
    with Repository(DEFAULT, metadataset="mds_oeh") as repo:
        # Which metadata sets exist at all? The choice changes what is
        # filterable and what gets found.
        print("Metadata sets of this instance:")
        for mds in repo.metadatasets():
            marker = " <- in use" if mds.id == repo.metadataset else ""
            print(f"  {mds.id:<24} {mds.name}{marker}")

        # 'Biologie' is a label. The library translates it into the URI THIS
        # instance carries for it.
        print()
        print(f"Search: {topic!r}, narrowed to the subject Biologie")
        result = repo.search(topic, subject="Biologie", limit=5,
                             facets=["ccm:educationalcontext"])

        # If a filter could not be resolved, the result is broader than asked
        # for -- which should be said, not swallowed.
        for unresolved in result.unresolved:
            print(f"  ! {unresolved}")

        print(f"  {result.total} hits in total, the first {len(result.hits)}:")
        for hit in result.hits:
            subjects = ", ".join(hit.labels("ccm:taxonid")) or "-"
            print(f"    {hit.title}")
            print(f"      {subjects} | {hit.url}")

        if result.facets:
            facet = result.facets[0]
            print()
            print(f"  Distribution by {facet.property}:")
            for value in facet.values[:5]:
                print(f"    {value.count:>5}x  {value.value.rsplit('/', 1)[-1]}")
            if facet.truncated:
                print(f"    (truncated -- {facet.other_count} more)")

        # Collections need both routes: for some search terms they share not a
        # single hit.
        print()
        print(f"Collections for {topic!r}:")
        collections = repo.find_collections(topic, limit=5)
        for warning in collections.warnings:
            print(f"  ! {warning}")
        for hit in collections.hits:
            print(f"    {hit.title} -- {hit.url}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(*sys.argv[1:2]))
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
