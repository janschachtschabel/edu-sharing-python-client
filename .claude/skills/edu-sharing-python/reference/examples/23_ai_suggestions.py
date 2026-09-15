"""Use case: the model proposes keywords, a program takes the best one over.

    EDU_SHARING_USER=... EDU_SHARING_PASSWORD=... B_API_KEY=... \\
        python docs/examples/23_ai_suggestions.py

Creates a throwaway folder of its own, works exclusively inside it, and removes
it afterwards. Without ``B_API_KEY`` it says what it would have done and stops;
without an account nothing can be written, and it says that too.

The editorial loop of the b-api's template mode, end to end:

1. **The model proposes.** ``BapiTemplates.suggest`` asks the configuration
   ``suggestion_ai`` for keywords and stores them as *pending suggestions* on
   the node -- the same records a person creates with
   ``node.suggestions.propose``. Nothing is written into the node itself.
2. **Something decides.** Here: the proposal with the highest ``confidence``.
   In an editorial tool: a person.
3. **``repo.flows.accept_suggestion`` takes it over** -- writes the keyword,
   reads it back, and only then marks the proposal ``ACCEPTED``. The others
   stay ``PENDING``.

Measured against staging on 2026-09-11, in two runs: eight and seven
proposals, confidence between 0.95 and 0.83, and the accepted one on the node
afterwards.

**The node must be readable by the gateway's own account.** A private one
answers 403, whatever ``user`` names -- the owner included. That is why the
throwaway material is published before the model is asked.
"""

import asyncio
import os
import sys
import uuid

from edusharing import AsyncRepository, EduSharingError
from edusharing.bapi import BapiTemplates
from edusharing.nodes import Node

# The Windows console otherwise emits cp1252 and mangles umlauts.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- Configuration ---------------------------------------------------
# Staging is filled in for the repository and the gateway, so this example runs
# as it stands; anything set in the environment wins. The key and the account
# are not, because they do not belong in a file.
REPOSITORY = os.environ.get(
    "EDU_SHARING_URL", "https://repository.staging.openeduhub.net")
METADATA_SET = os.environ.get("EDU_SHARING_METADATASET", "mds_oeh")
B_API = os.environ.get("B_API_BASE_URL", "https://b-api.staging.openeduhub.net")
B_API_KEY = os.environ.get("B_API_KEY", "")
USER = os.environ.get("EDU_SHARING_USER", "")
PASSWORD = os.environ.get("EDU_SHARING_PASSWORD", "")
LOGIN = (USER, PASSWORD) if USER else None

TITLE = "Photosynthese bei Pflanzen"
DESCRIPTION = ("Wie Pflanzen aus Licht, Wasser und Kohlenstoffdioxid Zucker und "
               "Sauerstoff bilden.")
#: The configuration that knows how to propose, and the field to propose for.
#: Every widget configuration in ``mds_oeh`` has the id ``default`` (measured).
CONFIGS = ["suggestion_ai"]
WIDGET = "cclom:general_keyword"


async def propose_and_accept(repo: AsyncRepository, templates: BapiTemplates,
                             node: Node) -> None:
    """Let the model propose, take the best proposal over, show what is left."""
    proposals = await templates.suggest(
        CONFIGS, {WIDGET: "default"}, context_node_id=node.id,
        variables={"cclom:title": TITLE, "cclom:general_description": DESCRIPTION})
    proposals.sort(key=lambda p: -(p.confidence or 0))
    print(f"{len(proposals)} proposals, stored as pending suggestions:")
    for proposal in proposals:
        print(f"  {proposal.confidence or 0:.2f}  {proposal.value}"
              f"  ({proposal.status}, by {proposal.author})")
    if not proposals:
        return

    best = proposals[0]
    result = await repo.flows.accept_suggestion(node.id, best.id)
    print(f"\naccepted {best.value!r}: applied={result['applied']}, "
          f"status={result['status']}")
    fresh = await repo.node(node.id)
    pending = [s for s in await fresh.suggestions.list() if s.status == "PENDING"]
    print(f"keywords on the node now: {fresh.keywords}")
    print(f"still pending: {len(pending)} -- nothing is taken over unasked")


async def main() -> int:
    if not B_API_KEY:
        print(f"B_API_KEY not set — nothing is asked of {B_API}.")
        print("It would create a throwaway material, let the model propose "
              "keywords for it, and take the best one over.")
        return 0

    async with AsyncRepository(REPOSITORY, metadataset=METADATA_SET,
                               auth=LOGIN) as repo:
        who = await repo.whoami()
        if who.is_anonymous:
            print("Writing needs an account. Please set EDU_SHARING_USER and "
                  "EDU_SHARING_PASSWORD.", file=sys.stderr)
            return 1

        folder = await repo.create_node(
            who.home_folder, name=f"example-{uuid.uuid4().hex[:8]}",
            type="cm:folder")
        try:
            node = await repo.create_node(folder.id, name="photosynthese.txt",
                                          title=TITLE)
            # The gateway reads the node with its own account: private -> 403.
            await node.permissions.publish()
            print(f"material: {node.url}\n")
            async with BapiTemplates(B_API_KEY, base_url=B_API,
                                     metadataset=METADATA_SET) as templates:
                await propose_and_accept(repo, templates, node)
        finally:
            await folder.delete(recycle=False)
            print("\nThrowaway folder removed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
