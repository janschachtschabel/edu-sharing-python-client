"""Use case: a prompt that lives on the server, filled from a collection.

    B_API_KEY=... python docs/examples/22_bapi_templates.py

Reads only -- nothing is written, neither to the repository nor anywhere else.
Without a key it prints what it would have asked and stops.

The b-api runs two ways. ``BildungsAPI`` (example 20) is the proxy: you send
the prompt. Here the prompt is a configuration in the metadata set, the one
the topic pages use; the caller names it, points at a context node and may fill
in values. ``BapiTemplates`` is its client, and it needs no ``BildungsAPI``.

Three calls, measured against staging on 2026-09-11:

1. **The chain as the topic pages run it.** The configuration reads
   ``{{var(cm:name)|node(cm:name)|-}}`` -- a value you pass, else the context
   node's own name. Nothing is passed, so the text is about the collection.
2. **The same with ``variables``.** Your value beats the node's. That is the
   feature, and the risk: free text goes into the prompt as it stands, and a
   value reading "ignore all previous instructions" steered the answer.
3. **``chat_limited`` with the same value.** The limited routes take
   ``{widget_id: value_id}`` pairs from a value space; ``cm:name`` has none,
   and the free text did not reach the prompt -- the text is about the
   collection again.

**The context node must be readable by the gateway's own account.** A private
node answers 403, whatever ``user`` names -- the owner included. A public
collection is used here for that reason.
"""

import asyncio
import os
import sys

from edusharing import AsyncRepository, EduSharingError
from edusharing.bapi import BapiTemplates

# The Windows console otherwise emits cp1252 and mangles umlauts.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- Configuration ---------------------------------------------------
# The repository holds the configurations (in its metadata set) and the
# context node; the gateway runs them. Staging is filled in for both; the key
# is not, because it does not belong in a file.
REPOSITORY = os.environ.get(
    "EDU_SHARING_URL", "https://repository.staging.openeduhub.net")
METADATA_SET = os.environ.get("EDU_SHARING_METADATASET", "mds_oeh")
B_API = os.environ.get("B_API_BASE_URL", "https://b-api.staging.openeduhub.net")
B_API_KEY = os.environ.get("B_API_KEY", "")

TOPIC = "Biologie"
#: The provider, the model, the message -- each later configuration overrides
#: the earlier, so the three together make one request.
CHAIN = ["topic_page_ai_default", "topic_page_ai_chat_completion",
         "topic_page_ai_text_widget"]
VALUE = "Vulkane"
#: What an answer about the value would contain: Vulkan, Vulkane, Vulkanen.
VALUE_STEM = "vulkan"


def short(text: str) -> str:
    return " ".join(text.split())[:150]


async def find_context() -> dict | None:
    """A public collection -- the gateway reads it with its own account."""
    async with AsyncRepository(REPOSITORY, metadataset=METADATA_SET) as repo:
        found = await repo.flows.find_collections(TOPIC, limit=1)
    return found["hits"][0] if found["hits"] else None


async def main() -> int:
    if not B_API_KEY:
        print(f"B_API_KEY not set — nothing is asked of {B_API}.")
        print(f"It would fill the configuration chain {CHAIN} from a public "
              f"{TOPIC!r} collection, three times.")
        return 0

    collection = await find_context()
    if collection is None:
        print(f"no collection for {TOPIC!r} — nothing to use as context")
        return 0
    node_id = collection["id"]
    print(f"context: {collection['title']}  ({node_id})")
    print()

    async with BapiTemplates(B_API_KEY, base_url=B_API,
                             metadataset=METADATA_SET) as templates:
        text = await templates.chat(CHAIN, context_node_id=node_id)
        print(f"1  from the node:         {short(text)}")

        text = await templates.chat(CHAIN, context_node_id=node_id,
                                    variables={"cm:name": VALUE})
        print(f"2  with variables:        {short(text)}")

        text = await templates.chat_limited(CHAIN, context_node_id=node_id,
                                            choices={"cm:name": VALUE})
        print(f"3  limited, same value:   {short(text)}")
        reached = VALUE_STEM in text.lower()
        print(f"   {VALUE!r} {'REACHED' if reached else 'did not reach'} "
              f"the prompt through the limited route")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
