"""Discover an MDS and reuse its vocabularies without fixed application fields.

Uses EDU_SHARING_URL / EDU_SHARING_METADATASET / optional credentials.
--profile accepts JSON keys matching MetadataProfile; absent means neutral.
Example profile: {"field_aliases": {"subject": "acme:subject"},
"read_fields": {"title": ["acme:title"]},
"write_fields": {"title": ["acme:title"]}}. These are illustrative fields,
not a schema assumed by the library. No repository writes.
"""

import argparse
import asyncio
import json
import os
from pathlib import Path

from edusharing import AsyncRepository, MetadataProfile


async def inspect_metadata(repo: AsyncRepository) -> dict:
    fields = await repo.metadata.fields()
    for field in fields:
        print(field["id"], field.get("caption"), field.get("isRequired"))
    properties = [field["id"] for field in fields if field.get("hasValues")][:5]
    values = await repo.vocab.preload(properties, concurrency=4)
    for prop, entries in values.items():
        print(prop, [(entry.uri, entry.label) for entry in entries[:3]])
    # This id is local to the example. A shared cache must use the actual
    # visibility/account scope consistently, never mix authenticated users.
    snapshot = json.loads(json.dumps(repo.vocab.snapshot(scope="example-session")))
    repo.vocab.clear_cache()
    print("Restored entries:", repo.vocab.restore(snapshot, scope="example-session"))
    return snapshot


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, help="MetadataProfile configuration as JSON")
    args = parser.parse_args()
    if not os.environ.get("EDU_SHARING_URL"):
        print("Set EDU_SHARING_URL and EDU_SHARING_METADATASET to inspect your repository.")
        return 0
    config = json.loads(args.profile.read_text(encoding="utf-8")) if args.profile else {}
    async with AsyncRepository.from_env(metadata_profile=MetadataProfile(**config)) as repo:
        await inspect_metadata(repo)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
