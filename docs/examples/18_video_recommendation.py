"""Use case: the ten best videos on a topic, then a model that recommends one.

    python docs/examples/18_video_recommendation.py
    B_API_KEY=... python docs/examples/18_video_recommendation.py

Reads only. The search runs anonymously; the recommendation needs a gateway
key and is skipped without one, with the table printed either way.

Three things worth watching:

* **The filter is a vocabulary value, not a free word.** ``type="Video"`` is one
  of the 48 values this instance offers for ``ccm:oeh_lrt_aggregated``.
  ``unresolved`` says whether it was applied -- a filter that was silently
  dropped answers a wider question than the one asked.
* **Reranking earns its keep on a human's phrasing.** ``rerank=True`` expands
  the query and re-scores a larger pool, at the cost of several requests.
* **The titles go into a model context, so they are marked as data.** They were
  written by strangers; ``as_untrusted`` keeps a description that says "ignore
  your instructions" from reading like one.
"""

import asyncio
import os
import sys

from edusharing import AsyncRepository, EduSharingError
from edusharing.agent import as_untrusted, one_line
from edusharing.bapi import BildungsAPI

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
# The metadata set decides more than the field names. Measured 2026-08-31
# against staging, the same query with the same filter: mds_oeh reports 1108
# hits, mds reports 14 -- and both report unresolved=[], so both applied the
# filter. Two indexes, two answers; which one is right depends on what you are
# looking for.
METADATA_SET = os.environ.get("EDU_SHARING_MDS", "mds_oeh")

# Left empty on purpose: the search below reads, and reading works anonymously.
USER = os.environ.get("EDU_SHARING_USER", "")
PASSWORD = os.environ.get("EDU_SHARING_PASSWORD", "")
LOGIN = (USER, PASSWORD) if USER else None

# The LLM gateway is a service of its own, with an address of its own, and the
# library carries no default -- a wrong one would send the key to a host nobody
# chose. Staging is filled in here as an example, and the key is not: it does
# not belong in a file.
B_API = os.environ.get("B_API_BASE_URL", "https://b-api.staging.openeduhub.net")
B_API_KEY = os.environ.get("B_API_KEY", "")

# Which provider and model. Nothing about them is hard-wired in the library:
# the OpenAI side of the gateway carries gpt-5.6-luna, the AcademicCloud side
# carries other ids entirely. Ask `await llm.load(provider)` to see the list.
PROVIDER = os.environ.get("B_API_PROVIDER", "openai")
MODEL = os.environ.get("B_API_MODEL", "gpt-5.6-luna")

TOPIC = "Bruchrechnung"
CONTENT_TYPE = "Video"
HOW_MANY = 10


def print_table(hits: list[dict]) -> None:
    """The ten, as a table that fits a terminal."""
    print(f"{'#':>2}  {'Title':<46}  {'Level':<22}  Subject")
    print("-" * 96)
    for rank, hit in enumerate(hits, start=1):
        fields = hit["fields"]
        title = one_line(hit["title"])
        level = ", ".join(fields.get("level") or []) or "—"
        subject = ", ".join(fields.get("subject") or []) or "—"
        print(f"{rank:>2}  {title[:46]:<46}  {level[:22]:<22}  {subject[:24]}")


def print_caveats(answer: dict) -> None:
    """What the numbers do and do not say. Reading a result without this is
    how a lower bound gets reported as a fact."""
    print()
    print(f"{answer['returned']} of {answer['total']} hits"
          f"{' (at least — a lower bound)' if answer['total_is_lower_bound'] else ''}"
          f", {answer['duplicates_removed']} folded as duplicates")
    if answer["unresolved"]:
        print("  NOT applied, so the answer is wider than asked:")
        for gap in answer["unresolved"]:
            print(f"    {gap['field']}={gap['value']!r}"
                  f"  did you mean: {', '.join(gap['suggestions']) or '(nothing)'}")
    else:
        print(f"  filter type={CONTENT_TYPE!r} was applied")


def as_material(hits: list[dict]) -> str:
    """The hits as text for a model -- marked as data, not as instructions.

    Every line here was written by somebody else. Wrapping it is what keeps a
    description that says "ignore your instructions" from reading like one.
    """
    zeilen = []
    for rank, hit in enumerate(hits, start=1):
        beschreibung = one_line(hit["description"] or "")[:220]
        zeilen.append(
            f"{rank}. {one_line(hit['title'])}\n"
            f"   Level: {', '.join(hit['fields'].get('level') or []) or 'unknown'}\n"
            f"   {beschreibung or '(no description)'}"
        )
    return as_untrusted("\n".join(zeilen), label="search results")


async def recommend(material: str) -> None:
    """The last step, and the only one that needs a key."""
    if not B_API_KEY:
        print()
        print("(B_API_KEY not set — the recommendation is skipped.)")
        print(f"The prompt would be {len(material)} characters long.")
        return

    async with BildungsAPI(B_API_KEY, base_url=B_API, provider=PROVIDER) as llm:
        antwort = await llm.chat(
            "Below is a list of videos from a search. Recommend ONE of them "
            "for a year 6 class and say in two sentences why. Name anything "
            "in the list that does not belong to the topic at all.\n\n"
            f"{material}",
            model=MODEL,
            system="Du antwortest knapp und auf Deutsch.",
            max_tokens=400,
        )
    print()
    print(f"--- Recommendation from {MODEL} via {PROVIDER} ---")
    print(antwort.strip())


async def main() -> int:
    async with AsyncRepository(
            REPOSITORY, metadataset=METADATA_SET, auth=LOGIN) as repo:
        answer = await repo.flows.search(
            TOPIC, type=CONTENT_TYPE, limit=HOW_MANY, rerank=True)

    hits = answer["hits"]
    print(f"{TOPIC!r}, filtered to {CONTENT_TYPE!r}, reranked — "
          f"against {REPOSITORY}")
    print()
    if not hits:
        print("No hits. Nothing to recommend.")
        return 0

    print_table(hits)
    print_caveats(answer)
    await recommend(as_material(hits))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
