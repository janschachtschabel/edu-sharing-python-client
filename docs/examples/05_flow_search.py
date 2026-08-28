"""Use case: find material and hand it on as JSON.

    EDU_SHARING_URL=https://repository.staging.openeduhub.net \
        python docs/examples/05_flow_search.py

Reads only. No credentials required, though signing in usually widens what is
visible.

The point of the flow level: three questions a tool actually asks --
*what is there*, *what may I filter by*, *tell me more about this one* -- each
answered in one call, each answering in JSON.

The API level can do all of it too, and returns objects instead. Use that one
when writing Python; use this one when passing the result onwards.
"""

import json
import os
import sys

from edusharing import EduSharingError, NotFoundError, Repository

# The Windows console otherwise emits cp1252 and mangles umlauts.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

METADATA_SET = os.environ.get("EDU_SHARING_MDS", "mds_oeh")


def show_vocabulary(repo: Repository) -> None:
    """What values may I filter by?

    Ask before guessing: a made-up subject silently returns everything.
    """
    subjects = repo.flows.vocabulary("subject")
    print(f"'subject' accepts {subjects['count']} values "
          f"(property {subjects['property']}), among them:")
    print("   ", ", ".join(subjects["values"][:8]), "...")


def run_search(repo: Repository) -> dict:
    """Search, and say what of the request did not survive.

    "Biologie" is a label, not a URI. It is resolved against this instance's
    own metadata set.
    """
    result = repo.flows.search("Photosynthese", subject="Biologie", limit=3)
    print(f"Query: {result['query']['text']!r} "
          f"filtered by {result['query']['filters']}")
    print(f"{result['total']} hits, showing {result['returned']}")
    print()

    # THE check: a filter that could not be resolved was not sent, and the
    # result is broader than asked for -- while looking complete.
    for item in result["unresolved"]:
        print(f"  ! {item['field']}={item['value']!r} unknown"
              f" -- did you mean: {', '.join(item['suggestions'][:3])}?")

    for hit in result["hits"]:
        print(f"  {hit['title']}")
        print(f"    {hit['url']}")
        # Readable values, not URIs -- and the keys are the short names.
        for field, values in hit["fields"].items():
            print(f"    {field}: {', '.join(values)}")
        print()
    return result


def describe_first(repo: Repository, hits: list) -> None:
    """Everything about one hit, in one call.

    Measured on 2026-08-27: 4 of 25 hits are not retrievable -- the index holds
    nodes that no longer exist. A chained tool has to survive that.
    """
    for hit in hits:
        try:
            details = repo.flows.describe(hit["id"])
        except NotFoundError:
            print(f"  (indexed but gone: {hit['id']})")
            continue
        print(f"Details for {details['title']!r}:")
        print(f"  type      {details['type']}")
        print(f"  access    {', '.join(details['access'])}")
        print(f"  keywords  {', '.join(details['keywords']) or '-'}")
        print(f"  {len(details['properties'])} raw properties available")
        return


def dump_json(result: dict) -> None:
    """What a tool passes on. No conversion step in between."""
    print()
    print("As JSON (truncated):")
    print(json.dumps(result, ensure_ascii=False, indent=2)[:400], "...")


def main() -> int:
    with Repository.from_env(metadataset=METADATA_SET) as repo:
        show_vocabulary(repo)
        print()
        result = run_search(repo)
        if not result["hits"]:
            print("No hits, nothing left to describe.")
            return 0
        describe_first(repo, result["hits"])
        dump_json(result)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
