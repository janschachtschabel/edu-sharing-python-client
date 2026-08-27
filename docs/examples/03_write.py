"""Writing with a read-back check -- and what happens without one.

    EDU_SHARING_USER=... EDU_SHARING_PASSWORD=... python docs/examples/03_write.py

Creates a throwaway folder of its own, works exclusively inside it, and removes
it afterwards. Nothing that was already there is touched.

What is demonstrated is the finding this library is built around: edu-sharing
answers lost writes with HTTP 200.
"""

import sys
import uuid

# The Windows console otherwise emits cp1252 and mangles umlauts.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from edusharing import EduSharingError, Repository, SilentDropError

# The metadata set mds_oeh does not know this property -- it is what makes the
# silent drop visible.
NOT_IN_MDS = "ccm:oeh_collection_compendium_text"


def main() -> int:
    with Repository.from_env(metadataset="mds_oeh") as repo:
        who = repo.whoami()
        if who.is_anonymous:
            print("Nothing can be written without signing in. Please set "
                  "EDU_SHARING_USER and EDU_SHARING_PASSWORD.", file=sys.stderr)
            return 1
        print(f"Signed in as {who.display_name} ({who.authority})")
        print()

        folder = repo.create_node(
            who.home_folder, name=f"example-{uuid.uuid4().hex[:8]}", type="cm:folder",
            title="Throwaway folder of this example")
        print(f"Throwaway folder created: {folder.name}")

        try:
            node = repo.create_node(folder.id, name="material.txt", title="First title")
            print(f"  node:    {node.url}")

            # 1. A property the metadata set knows.
            node = node.update(title="Changed title",
                               description="Written by the library")
            print(f"  title:   {node.get('cclom:title')}")

            # 2. One it does not know -- the server reports 200 and stores nothing.
            try:
                node.update(properties={NOT_IN_MDS: "This text gets lost"})
                print("  ! No error -- that would be surprising.")
            except SilentDropError as drop:
                print(f"  caught:  {', '.join(drop.dropped)} did not arrive")
                print("           (the server had reported 200)")

            # 3. The direct route bypasses the filtering -- deliberately, not
            #    automatically.
            node = node.set_property(NOT_IN_MDS, "Stored via the direct route")
            print(f"  direct:  {node.get(NOT_IN_MDS)}")

            # 4. Extend keywords, do not replace them: the list is shared.
            node = node.update(properties={"cclom:general_keyword": ["From someone else"]})
            node = node.add_keywords("Weimar (Ort)")
            print(f"  keywords: {node.keywords}")

            # 5. Attach a file and fetch it back.
            content = "An example text with umlauts: Größe, Übung.\n".encode()
            node = node.content.upload(content, filename="material.txt",
                                       mimetype="text/plain")
            back = node.content.download()
            print(f"  file:    {node.content.size} bytes, identical: {back == content}")

        finally:
            folder.delete()
            print()
            print("Throwaway folder removed -- the holdings are as they were found.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EduSharingError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
