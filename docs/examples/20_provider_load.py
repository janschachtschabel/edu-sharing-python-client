"""Use case: which model should answer, and on what basis.

    B_API_KEY=... python docs/examples/20_provider_load.py

Reads only, and only from the gateway -- no repository involved. Without a key
it prints what it would have asked and stops.

The two providers behind the same gateway are not interchangeable, and the
difference decides how you choose a model:

* **The AcademicCloud reports load.** ``demand`` moves by the minute, so a
  virtual model -- name two or three, take the least loaded -- is worth having.
* **OpenAI reports none.** Not for any of its 132 models, and no output types
  either. There is nothing to rank on, so ``chat()`` without a model **refuses**
  there rather than guessing. It used to guess: the ranking fell back to the
  model id, alphabetical order picked ``babbage-002``, a 2019 completion model,
  and the call failed after three attempts with an error that named none of
  this. That is the bug this example was written to keep fixed.

``load()`` is what tells the two apart. Ask it once at start-up, log
``summary()``, and whoever reads the log later knows what the choice was made
on. **Read ``reports_load`` before the ranking**: where it is false, the order
is alphabetical, not a statement about queues.
"""

import asyncio
import os
import sys

from edusharing.bapi import BildungsAPI
from edusharing.errors import EduSharingError

# The Windows console otherwise emits cp1252 and mangles umlauts.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- Configuration ---------------------------------------------------
# The gateway is a service of its own, with an address of its own, and the
# library carries no default -- a wrong one would send the key to a host nobody
# chose. Staging is filled in here as an example; the key is not, because it
# does not belong in a file.
B_API = os.environ.get("B_API_BASE_URL", "https://b-api.staging.openeduhub.net")
B_API_KEY = os.environ.get("B_API_KEY", "")

PROVIDERS = ("academiccloud", "openai")
QUESTION = "Nenne genau drei Stichworte zur Bruchrechnung, kommasepariert."


async def report(provider: str) -> None:
    """What this provider says about itself, and whether it can be asked blind."""
    async with BildungsAPI(B_API_KEY, base_url=B_API, provider=provider) as llm:
        load = await llm.load()
        print(f"--- {provider}")
        print(f"  {len(load.models)} of {load.total} usable, "
              f"load reported: {load.reports_load}, "
              f"retired today: {len(load.retired)}")
        for model in load.models[:3]:
            demand = "  —" if model.demand is None else f"{model.demand:>3}"
            print(f"    demand={demand}  {model.id}")

        try:
            answer = await llm.chat(QUESTION, max_tokens=120)
        except EduSharingError as exc:
            # Not a failure of the example: at OpenAI this is the correct
            # answer, and saying so beats picking a model nobody chose.
            print(f"  automatic choice refused: {str(exc)[:96]}")
            return
        print(f"  automatic choice: {llm.last_model}")
        print(f"    {' '.join(answer.split())[:70]}")


async def virtual_model() -> None:
    """Name several, let the least loaded answer -- and the next one if not."""
    async with BildungsAPI(B_API_KEY, base_url=B_API,
                           provider="academiccloud") as llm:
        load = await llm.load()
        if len(load.models) < 2:
            print("\n(too few usable models for a group)")
            return
        group = [m.id for m in load.models[:3]]
        print(f"\n--- a group of {len(group)}: {', '.join(group)}")
        answer = await llm.chat(QUESTION, model=group, max_tokens=120)
        print(f"  answered: {llm.last_model}")
        print(f"    {' '.join(answer.split())[:70]}")


async def main() -> int:
    if not B_API_KEY:
        print(f"B_API_KEY not set — nothing is asked of {B_API}.")
        print("It would ask both providers for their model list and then one "
              "question each.")
        return 0

    for provider in PROVIDERS:
        await report(provider)
    await virtual_model()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
