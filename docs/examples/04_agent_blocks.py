"""Search, prepare, hand to a language model.

    B_API_KEY=... python docs/examples/04_agent_blocks.py [topic]

Shows the arc ``edusharing.agent`` exists for: a search becomes a model context
that keeps its citations, marks foreign content and stays within a budget.
Without the b-api key everything but the last step still runs.

None of this is MCP-specific -- an MCP server would be a thin adapter on top.
"""

import sys

# The Windows console otherwise emits cp1252 and mangles umlauts.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os

from edusharing import AsyncRepository, EduSharingError
from edusharing.agent import as_result, as_untrusted, format_results, is_safe_url
from edusharing.bapi import BildungsAPI

REPO = "https://repository.staging.openeduhub.net"


async def main(topic: str) -> int:
    async with AsyncRepository(REPO, metadataset="mds_oeh") as repo:
        # 1. Search -- as a tool result, so a failure does not end the whole run
        #    but becomes information.
        result = await as_result(
            repo.search(topic, subject="Biologie", limit=5),
            format=lambda r: format_results(r, max_chars=1500),
        )
        if not result:
            print(f"Search failed ({result.error_type}): {result.error}")
            return 1

        print("--- What the model would see ---")
        print(result.text)

        hits = result.data
        print()
        print(f"--- Citations survive: {len(hits.hits)} ---")
        for hit in hits.hits:
            print(f"  {hit.id}  {hit.url}")

        # 2. Check source URLs before anything fetches them.
        print()
        print("--- Source URLs checked (SSRF) ---")
        for hit in hits.hits[:3]:
            source = hit.source_url
            if source:
                mark = "ok " if is_safe_url(source) else "BLOCKED"
                print(f"  {mark} {source[:70]}")

        if not hits.hits:
            print()
            print("No hits -- without material there is no model context.")
            return 0

        # 3. Foreign text goes into the prompt marked as such.
        material = "\n\n".join(
            as_untrusted(h.description or h.title, label=f"Material {h.id}")
            for h in hits.hits[:3]
        )

        if not os.environ.get("B_API_KEY"):
            print()
            print("(B_API_KEY not set -- the model call is skipped.)")
            print(f"The prompt would be {len(material)} characters long.")
            return 0

        async with BildungsAPI.from_env() as llm:
            answer = await llm.chat(
                f"Summarise in one sentence what these materials are about:"
                f"\n\n{material}",
                system="You answer briefly and in German.",
                max_tokens=200,
            )
            print()
            print(f"--- Answer from {llm.last_model} ---")
            print(answer.strip())

    return 0


if __name__ == "__main__":
    import asyncio

    subject = sys.argv[1] if len(sys.argv) > 1 else "Photosynthese"
    try:
        raise SystemExit(asyncio.run(main(subject)))
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
