"""Use case: the editorial round — comment, rate, propose, hand over.

    EDU_SHARING_USER=... EDU_SHARING_PASSWORD=... \\
        python docs/examples/16_editorial.py

Creates a throwaway folder of its own, works exclusively inside it, and removes
it afterwards. Nothing that was already there is touched.

These are the four surfaces an editorial application uses and the flow level
does not cover: `node.comments`, `node.rating`, `node.suggestions` and
`node.workflow`. None of them has a flow, and that is deliberate — each stays
with one endpoint family, while a flow earns its place by composing several.

Four measured behaviours it demonstrates rather than describes:

* a rating of `0` is a **vote**, not a reset — it lowers the average;
* accepting a suggestion does **not** write the value onto the node;
* the workflow history is **newest first**;
* a comment is stored byte for byte, so it is sent as raw UTF-8.
"""

import sys
import uuid

from edusharing import EduSharingError, Repository

# The Windows console otherwise emits cp1252 and mangles umlauts.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

#: WLO's first editorial step. The vocabulary belongs to the instance, so this
#: is the one value in this file another repository will not know.
SUBMIT_STATUS = "100_tocheck"


def main() -> int:
    with Repository.from_env(metadataset="mds_oeh") as repo:
        who = repo.whoami()
        if who.is_anonymous:
            print("None of this works anonymously. Please set EDU_SHARING_USER "
                  "and EDU_SHARING_PASSWORD.", file=sys.stderr)
            return 1
        print(f"Signed in as {who.display_name} ({who.authority})\n")

        folder = repo.create_node(
            who.home_folder, name=f"example-{uuid.uuid4().hex[:8]}",
            type="cm:folder")
        try:
            node = repo.create_node(folder.id, name="material.txt",
                                    title="Photosynthese, kurz erklärt")
            print(f"material: {node.url}\n")
            _comments(node)
            _rating(node)
            _suggestions(repo, node)
            _workflow(node, who.authority)
        finally:
            folder.delete()
            print("\nThrowaway folder removed.")

    return 0


def _comments(node) -> None:
    print("--- comments " + "-" * 52)
    first = node.comments.add("Nice, but the source is missing.")
    node.comments.add("Which source do you mean?", reply_to=first.id)
    node.comments.edit(first.id, "Nice, but the source is missing. (edited)")

    for comment in node.comments.list():
        kind = f"reply to {comment.reply_to[:8]}" if comment.reply_to else "top level"
        print(f"  {comment.text[:48]:50s} {kind}")
    print("  Stored byte for byte — sent as JSON, the quotes would land in the")
    print("  text. That is why the library sends raw UTF-8.")


def _rating(node) -> None:
    print("\n--- rating " + "-" * 54)
    # rate() returns the new summary; `node.rating` still holds what the node
    # carried when it was loaded.
    after = node.rate(5)
    print(f"  rate(5)   -> average {after.average}, {after.count} vote(s), "
          f"own {after.own}")

    try:
        node.rate(0)
    except ValueError as exc:
        print(f"  rate(0) refused: {str(exc)[:62]}…")
        print("  Measured: a 0 counts as a vote and lowers the average. The")
        print("  Ideendatenbank documents it as a reset; it is not one.")

    back = node.unrate()
    # None, not a zero average: with no votes left there is no summary to
    # report, and a 0.0 would read as "everyone rated it badly".
    print(f"  unrate()  -> {back!r}")
    print("  None means no votes left — not an average of zero.")


def _suggestions(repo, node) -> None:
    print("\n--- suggestions " + "-" * 49)
    # One property, one value, and a reason -- the reason is mandatory here and
    # upstream: a proposal nobody can weigh is not reviewable, and reviewing is
    # the whole point.
    made = node.suggestions.propose(
        "cclom:general_keyword", "Zellbiologie",
        "Der Text handelt durchgehend von Zellen.", confidence=0.8)
    print(f"  proposed: {made.property} = {made.value!r}  status {made.status}")
    pending = node.suggestions.list()

    node.suggestions.decide([s.id for s in pending], accept=True)
    print(f"  after deciding:   {[s.status for s in node.suggestions.list()]}")
    # Read the node again -- the object in hand still carries what it was
    # loaded with.
    print(f"  keywords on the node: {repo.node(node.id).keywords}")
    print("  Accepting marks the suggestion — it does NOT write the value.")
    print("  An application that expects otherwise loses the data silently.")


def _workflow(node, receiver: str) -> None:
    print("\n--- workflow " + "-" * 52)
    try:
        # The receiver comes first and is required: a queue nobody owns is not
        # a handover.
        node.workflow.submit(receiver, SUBMIT_STATUS, "Please check the source.")
    except EduSharingError as exc:
        print(f"  submit refused: {type(exc).__name__} — {str(exc)[:46]}")
        print(f"  {SUBMIT_STATUS!r} is this instance's vocabulary; another")
        print("  repository uses different values.")
        return

    for step in node.workflow.history():
        print(f"  {step.status:14s} {step.comment[:30]:32s} "
              f"{step.at:%Y-%m-%d %H:%M}  -> {', '.join(step.receivers)}")
    print("  Newest first — measured by submitting twice. A read-back that")
    print("  reversed the list would return the older of two identical steps.")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
