"""Prepare a material draft and/or load collection context, without writes.

Run with --url https://example.org/material --title 'A title' and/or
--collection <id>. Uses the repository environment variables. The default
profile is WLO-compatible; --profile supplies MetadataProfile JSON for another
metadata set. Review readiness, duplicate status and partial errors yourself.
"""

import argparse
import asyncio
import json
import os
from pathlib import Path

from edusharing import AsyncRepository, MetadataProfile


async def prepare_and_context(
    repo: AsyncRepository, *, url: str | None = None,
    title: str | None = None, collection_id: str | None = None,
) -> dict:
    result = {}
    if url:
        result["prepared"] = await repo.flows.prepare_material(url, title=title)
    if collection_id:
        result["context"] = await repo.flows.collection_context(collection_id, limit=10)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url")
    parser.add_argument("--title")
    parser.add_argument("--collection")
    parser.add_argument("--profile", type=Path)
    args = parser.parse_args()
    if not os.environ.get("EDU_SHARING_URL") or not (args.url or args.collection):
        print("Set EDU_SHARING_URL / EDU_SHARING_METADATASET, then pass --url or --collection.")
        return 0
    profile = (MetadataProfile(**json.loads(args.profile.read_text(encoding="utf-8")))
               if args.profile else None)
    async with AsyncRepository.from_env(metadata_profile=profile) as repo:
        await prepare_and_context(repo, url=args.url, title=args.title,
                                  collection_id=args.collection)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
