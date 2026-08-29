"""Use case: the full text of a material, from wherever it is available.

    EDU_SHARING_TEXT_EXTRACTION_URL=https://... \\
        python docs/examples/15_full_text.py [topic]

Reads only. Nothing is created, changed or deleted. Without the extraction
service everything but the fallback still runs, and the script says how many
materials it could not have answered for.

**Two sources, and neither covers the other.** A repository stores the full text
of the files it *hosts*. For material that only links somewhere (`ccm:wwwurl`)
it has nothing, because the page is not its file — that is what the extraction
service beside it is for. Measured the other way round too: an edu-sharing
download URL handed to the service answers 424. Each source knows what the
other does not.

There is no flow for this. A flow earns its place by composing several endpoint
families; this composes one repository call with a second *service*, and which
service that is, is the caller's configuration, not the repository's.
"""

import asyncio
import os
import sys
from typing import NamedTuple

from edusharing import (
    AsyncRepository,
    EduSharingError,
    NotFoundError,
    PermissionDeniedError,
)
from edusharing.extraction import TextExtraction

# The Windows console otherwise emits cp1252 and mangles umlauts.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- Configuration ---------------------------------------------------
# Point these at your own repository. The values below are the staging
# instance, filled in so this example runs as it stands; anything set in the
# environment wins over them. Configured once, here -- no call below takes an
# address of its own.
STAGING = "https://repository.staging.openeduhub.net"
REPOSITORY = os.environ.get("EDU_SHARING_URL", STAGING)
METADATA_SET = os.environ.get("EDU_SHARING_MDS", "mds_oeh")

# Left empty on purpose: without them the example runs anonymously, which is
# enough for reading. Writing needs both -- fill them in, or set
# EDU_SHARING_USER and EDU_SHARING_PASSWORD in the environment.
USER = os.environ.get("EDU_SHARING_USER", "")
PASSWORD = os.environ.get("EDU_SHARING_PASSWORD", "")
LOGIN = (USER, PASSWORD) if USER else None

# The extraction service is a service of its own, with an address of its
# own. Staging's is filled in -- but ONLY while the repository above is
# staging too. Pairing your own repository with somebody else's extraction
# service would send your material URLs to a host you did not choose, and
# that is exactly why the library carries no default for it.
EXTRACTION = os.environ.get(
    "EDU_SHARING_TEXT_EXTRACTION_URL",
    "https://text-extraction.staging.openeduhub.net"
    if REPOSITORY == STAGING else "")

LIMIT = 8


class Tally(NamedTuple):
    """What the table saw, for the two notes that follow it."""

    gaps: int
    used_service: bool
    a_linked_url: str


def announce_missing_service() -> None:
    """Say what is skipped, and why there is no default to fall back on."""
    print(f"({TextExtraction.ENV_BASE_URL} not set — the fallback is skipped.")
    print(" There is no default on purpose: each installation runs its own")
    print(" service, and a default pointing at somebody else's sends your")
    print(" material URLs into an environment you did not choose.)")
    print()


async def report_rows(
    repo: AsyncRepository, hits: list, service: TextExtraction | None
) -> Tally:
    """One row per material: what the repository has, what the service adds."""
    print(f"{'material':34s} {'repository':>10s} {'service':>18s}")
    print("-" * 66)
    gaps = 0
    used_service = False
    linked_seen = ""
    for hit in hits:
        try:
            node = await repo.nodes.get(hit.id)
        except NotFoundError:
            # The search index outlives its nodes -- measured, 4 of 25.
            print(f"{hit.title[:32]:34s} {'gone':>10s}")
            continue

        try:
            stored = await node.content.text()
        except PermissionDeniedError:
            # Measured 2026-08-28 against redaktion.openeduhub.net: an
            # anonymous caller may *find* material whose content it may not
            # *read*. Treated like "no stored text" -- the metadata came back,
            # so the linked address is there and the service can still answer.
            # Letting it raise would end the run over one refused row.
            stored, refused = None, True
        else:
            refused = False

        linked = node.get("ccm:wwwurl")
        column = f"{'refused':>10s}" if refused else f"{len(stored or ''):>10d}"
        linked_seen = linked_seen or (linked or "")

        if stored or not linked:
            print(f"{node.title[:32]:34s} {column}")
            continue

        if service is None:
            gaps += 1
            print(f"{node.title[:32]:34s} {column} {'(needs service)':>18s}")
            continue

        got = await service.text_of(linked, max_chars=20_000)
        used_service = True
        # No text is a normal outcome, not an error -- `reason` says which.
        answer = f"{got.char_count} chars" if got.text else f"none: {got.reason}"
        print(f"{node.title[:32]:34s} {column} {answer:>18s}")
        if got.text:
            print(f"    {got.lang}  “{got.text[:70].strip()}…”")
        elif got.detail:
            print(f"    {got.detail[:60]}")
    return Tally(gaps, used_service, linked_seen)


async def demonstrate_service(service: TextExtraction, url: str) -> None:
    """Run the service even though nothing needed it.

    Whether a hit needs the fallback depends on the day's index, and an example
    whose point shows up only sometimes teaches it only sometimes.
    """
    print("No material here needed the fallback, so the service ran on a")
    print("linked address of one of them anyway — to make its answer visible:")
    shown = await service.text_of(url, max_chars=20_000)
    print(f"    {url[:60]}")
    if shown.text:
        print(f"    {shown.lang}  {shown.char_count} chars  "
              f"“{shown.text[:60].strip()}…”")
    else:
        print(f"    no text: {shown.reason} — {shown.detail[:50]}")
    print()


def closing_note(service: TextExtraction | None, gaps: int) -> None:
    """What the zeros in the table do and do not mean."""
    if service is None and gaps:
        print(f"{gaps} of these carry no stored text and link elsewhere. Without the")
        print("service this library cannot answer for them — and an empty")
        print("`content.text()` would look like an empty page rather than a gap.")
    elif service is None:
        print("Every material here had stored text, so nothing was missed.")
    else:
        print("A zero in the repository column is not an empty file: Markdown and")
        print("JSON are not extracted at all (measured), and for linked material")
        print("there is nothing to extract. `content.download()` still has the bytes.")


async def main(topic: str = "Photosynthese") -> int:
    configured = bool(EXTRACTION)
    if not configured:
        announce_missing_service()

    async with AsyncRepository(REPOSITORY, metadataset=METADATA_SET, auth=LOGIN) as repo:
        result = await repo.search(topic, limit=LIMIT)
        if not result.hits:
            print(f"No material for {topic!r}.", file=sys.stderr)
            return 0

        service = TextExtraction(EXTRACTION) if configured else None
        try:
            tally = await report_rows(repo, result.hits, service)
            print()
            if service is not None and not tally.used_service and tally.a_linked_url:
                await demonstrate_service(service, tally.a_linked_url)
            closing_note(service, tally.gaps)
        finally:
            if service is not None:
                await service.aclose()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main(*sys.argv[1:2])))
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
