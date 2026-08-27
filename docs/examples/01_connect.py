"""Connect and see what you are dealing with.

    python docs/examples/01_connect.py
    python docs/examples/01_connect.py https://my-repository.example/edu-sharing

Runs without credentials. With ``EDU_SHARING_USER`` and ``EDU_SHARING_PASSWORD``
in the environment the example signs in and shows the difference.
"""

import sys

# The Windows console otherwise emits cp1252 and mangles umlauts. This affects
# only this example's output -- the library works in UTF-8 throughout and does
# not touch stdout.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from edusharing import BasicCredential, EduSharingError, Repository

DEFAULT = "https://repository.staging.openeduhub.net"


def main(url: str) -> int:
    with Repository(url, auth=BasicCredential.from_env()) as repo:
        print(f"Repository: {repo.url}")
        print()

        # What kind of instance is this? The answer decides what an application
        # may presuppose -- instead of guessing.
        about = repo.about()
        print(f"  edu-sharing    {about.repository_version}")
        print(f"  render service {about.renderservice_version}")
        print(f"  API            {about.api_version}")
        print(f"  services       {len(about.services)}")
        if about.plugins:
            print(f"  plugins        {', '.join(about.plugins)}")

        # Who am I running as? Without asking, an application does not notice
        # it is working as a guest -- and trips later somewhere unrelated to
        # the cause.
        who = repo.whoami()
        print()
        if who.is_anonymous:
            print("  Signed in as: nobody (anonymous access)")
            print("  For write access set EDU_SHARING_USER and EDU_SHARING_PASSWORD.")
        else:
            print(f"  Signed in as: {who.display_name} ({who.authority})")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT))
    except EduSharingError as exc:
        # Errors from this library are explained errors -- they need no
        # traceback to be understood.
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
