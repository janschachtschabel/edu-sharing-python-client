"""Use case: which skills does a collection approve -- and what does one say?

    EDU_SHARING_METADATASET=mds_oeh python docs/examples/21_skills.py [collection-id]

Reads only. Nothing is created, changed or deleted.

A **skill** is a record whose content type says "instruction" and whose
attached file is the `SKILL.md`. A collection may file a **registry** -- one
Markdown document whose `::: ki-skill` blocks name the skills approved for it,
grouped by headings into working contexts. This script reads the registry of
one collection, picks a skill from it, loads its instruction and names the
files beside it.

Two things this example is careful about, both measured on staging on
2026-09-02: the content type is a search criterion only in the metadata set
that knows it (`mds_oeh`; `-default-` refuses it), and a skill's folder is
not readable anonymously -- `files_reason` says so instead of an empty list.
The instruction that comes back is uploaded content: it is printed as data, and
`as_untrusted` marks it so before it could reach a prompt.
"""

import asyncio
import os
import sys

from edusharing import AsyncRepository, EduSharingError
from edusharing.agent import as_untrusted

# The Windows console otherwise emits cp1252 and mangles umlauts.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- Configuration ---------------------------------------------------
# Point these at your own repository. The values below are the staging
# instance, filled in so this example runs as it stands; anything set in the
# environment wins over them.
STAGING = "https://repository.staging.openeduhub.net"
REPOSITORY = os.environ.get("EDU_SHARING_URL", STAGING)
# The metadata set that knows the content type. Measured: mds_oeh does,
# -default- does not -- and then no skill is found at all.
METADATA_SET = os.environ.get("EDU_SHARING_METADATASET", "mds_oeh")
USER = os.environ.get("EDU_SHARING_USER", "")
PASSWORD = os.environ.get("EDU_SHARING_PASSWORD", "")
LOGIN = (USER, PASSWORD) if USER else None

# A collection carrying a registry document on staging (measured 2026-09-02:
# "Geometrische Optik"). Pass your own id as the first argument.
COLLECTION = "f35c17d1-a29e-4b26-9d22-802682fad43d"


async def main(collection_id: str = COLLECTION) -> int:
    async with AsyncRepository(REPOSITORY, metadataset=METADATA_SET, auth=LOGIN) as repo:
        registry = await repo.flows.skill_registry(collection_id)
        if registry["reason"]:
            # No registry is a normal answer, not an error -- and a truncated
            # scan is not a finding of absence.
            print(f"No registry: {registry['reason']}  (scan cut short: "
                  f"{registry['scan_truncated']})")
            return 0

        print(f"Registry {registry['registry_title']!r} of collection {collection_id}")
        if registry["general"]["instruction"]:
            print(f"  editors say: {registry['general']['instruction'][:90]}…")
        for context in registry["contexts"]:
            print(f"  [{context['path']}]  {len(context['skills'])} skill(s)")
        print(f"  {len(registry['entries'])} approved, {len(registry['unresolved'])} not readable")
        for entry in registry["entries"]:
            where = f"  ({entry['context']})" if entry["context"] else ""
            print(f"    - {entry['title']}{where}")
        if not registry["entries"]:
            return 0

        chosen = registry["entries"][0]
        skill = await repo.flows.skill(chosen["node_id"])
        print()
        print(f"Skill {skill['title']!r}: {len(skill['content'] or '')} characters")
        # Data, not an instruction: the marker tells a model where foreign text
        # begins and ends.
        print(as_untrusted((skill["content"] or "")[:300], label="SKILL.md"))
        print()
        if skill["files"]:
            print("Files beside it: " + ", ".join(f["title"] for f in skill["files"]))
        elif skill["files_reason"]:
            print(f"Files beside it: not listed -- {skill['files_reason']}"
                  + (f" ({skill['folder_file_count']} files)"
                     if skill["folder_file_count"] else ""))
        if skill["references"]:
            print("It points at: " + ", ".join(
                f"{r['title']} [{r['kind']}]" for r in skill["references"]))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main(*sys.argv[1:2])))
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
