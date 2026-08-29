"""Use case: a query phrased the way a person actually asks.

    EDU_SHARING_URL=https://repository.staging.openeduhub.net \
        python docs/examples/08_flow_rerank.py

Reads only. No credentials required.

edu-sharing ANDs every word of a query. Words that describe the *shape* of a
request rather than its subject -- "Arbeitsblatt", "ich suche", "Klasse 7" --
appear in almost no record, so a single one empties the result set.

That is exactly how a language model phrases things. Left alone it reports "no
material found" about a subject with fifteen hundred records, and a person
believes it. This script shows the gap and what `rerank=True` does about it.
"""

import os
import sys

from edusharing import EduSharingError, LanguageProfile, Repository

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

# Left: how a person asks. Right: the bare subject.
PAIRS = [
    ("Ich suche ein Arbeitsblatt zur Bruchrechnung", "Bruchrechnung"),
    ("Unterrichtsstunde Französische Revolution", "Französische Revolution"),
    ("Erklärvideo Photosynthese", "Photosynthese"),
]


def show_cost_of_framing(repo: Repository) -> None:
    """How much a framing word costs, asked both ways."""
    print("How much a framing word costs")
    print("=" * 72)
    print(f"{'as asked':>10}  {'subject only':>13}   query")
    for natural, subject in PAIRS:
        asked = repo.flows.search(natural, limit=1)
        bare = repo.flows.search(subject, limit=1)
        print(f"{asked['total']:>10}  {bare['total']:>13}   {natural!r}")


def show_rerank(repo: Repository) -> None:
    """What rerank=True recovers, one query variant per request."""
    print("What rerank=True recovers")
    print("=" * 72)
    for natural, _ in PAIRS:
        plain = repo.flows.search(natural, limit=3)
        ranked = repo.flows.search(natural, rerank=True, limit=3)
        print(f"\n{natural!r}")
        print(f"  without: {plain['returned']} results")
        print(f"  with   : {ranked['returned']} results "
              f"(variants asked: {', '.join(ranked['query']['variants'])})")
        for hit in ranked["hits"][:2]:
            print(f"     - {hit['title'][:62]}")


def show_total_is_a_lower_bound(repo: Repository) -> None:
    """The total comes from the variant that found something.

    Otherwise the answer would read "3 results, 0 found", which is
    contradictory.
    """
    ranked = repo.flows.search(PAIRS[0][0], rerank=True, limit=3)
    print(f"  total {ranked['total']} "
          f"(lower bound: {ranked['total_is_lower_bound']}) -- overlapping "
          "variants cannot be added up")


def measure_index_stability(repo: Repository) -> None:
    """Reranking does not make the search reproducible.

    That comes from the repository, not from the ranking -- so this measures
    rather than asserts: a single run may well come out stable.
    """
    runs = [
        {h["id"] for h in repo.flows.search("Photosynthese", limit=25)["hits"]}
        for _ in range(3)
    ]
    overlap = [len(runs[0] & other) for other in runs[1:]]
    print(f"  the same query three times, 25 hits each: "
          f"{overlap} of 25 in common with the first run")
    if min(overlap) < 25:
        print("  the index is not stable -- caching or comparing two runs "
              "has to account for that")
    else:
        print("  stable in this run; measured on 2026-08-27 it was not "
              "(10 of 25 in common), so do not rely on it")


def show_other_language(repo: Repository) -> None:
    """The word lists are German by default, not by assumption."""
    print("The word lists are German by default, not by assumption")
    print("=" * 72)
    english = LanguageProfile(
        stopwords=frozenset({"the", "of", "a", "an", "for"}),
        framing=frozenset({"worksheet", "video", "lesson", "need", "want"}),
        synonyms={},
    )
    result = repo.flows.search(
        "I need a worksheet about photosynthesis", rerank=True,
        language=english, limit=2)
    print(f"  English profile, variants asked: "
          f"{', '.join(result['query']['variants'])}")
    print(f"  {result['returned']} results")


def main() -> int:
    with Repository(REPOSITORY, metadataset=METADATA_SET, auth=LOGIN) as repo:
        show_cost_of_framing(repo)
        print()
        show_rerank(repo)
        print()
        print("Two limits, stated plainly")
        print("=" * 72)
        show_total_is_a_lower_bound(repo)
        measure_index_stability(repo)
        print()
        show_other_language(repo)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
