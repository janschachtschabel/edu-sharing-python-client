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

import sys

# The Windows console otherwise emits cp1252 and mangles umlauts.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os

from edusharing import AsyncRepository, EduSharingError, NotFoundError
from edusharing.extraction import TextExtraction

REPO = "https://repository.staging.openeduhub.net"
LIMIT = 8


async def main(topic: str) -> int:
    configured = bool(os.environ.get(TextExtraction.ENV_BASE_URL))
    if not configured:
        print(f"({TextExtraction.ENV_BASE_URL} not set — the fallback is skipped.")
        print(" There is no default on purpose: each installation runs its own")
        print(" service, and a default pointing at somebody else's sends your")
        print(" material URLs into an environment you did not choose.)")
        print()

    async with AsyncRepository(REPO, metadataset="mds_oeh") as repo:
        result = await repo.search(topic, limit=LIMIT)
        if not result.hits:
            print(f"No material for {topic!r}.", file=sys.stderr)
            return 0

        service = TextExtraction.from_env() if configured else None
        try:
            await _report(repo, result.hits, service)
        finally:
            if service is not None:
                await service.aclose()

    return 0


async def _report(repo, hits, service) -> None:
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

        stored = await node.content.text()
        linked = node.get("ccm:wwwurl")
        column = f"{len(stored or ''):>10d}"

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

    print()
    if service is not None and not used_service and linked_seen:
        # Whether a hit needs the fallback depends on the day's index, and an
        # example whose point shows up only sometimes teaches it only sometimes.
        print("No material here needed the fallback, so the service ran on a")
        print("linked address of one of them anyway — to make its answer visible:")
        shown = await service.text_of(linked_seen, max_chars=20_000)
        print(f"    {linked_seen[:60]}")
        if shown.text:
            print(f"    {shown.lang}  {shown.char_count} chars  "
                  f"“{shown.text[:60].strip()}…”")
        else:
            print(f"    no text: {shown.reason} — {shown.detail[:50]}")
        print()
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


if __name__ == "__main__":
    import asyncio

    subject = sys.argv[1] if len(sys.argv) > 1 else "Photosynthese"
    try:
        raise SystemExit(asyncio.run(main(subject)))
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
