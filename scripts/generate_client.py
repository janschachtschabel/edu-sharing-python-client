#!/usr/bin/env python3
"""Erzeugt die generierte Client-Schicht (``src/edusharing/_generated``).

Die edu-sharing-Spec laesst sich NICHT unveraendert generieren: 244 Pfad-Parameter
tragen einen ``schema.default`` (``-home-``, ``-default-``, ``-userhome-``), und
sobald danach ein Parameter ohne Default folgt, erzeugt der Generator ungueltiges
Python::

    def _get_kwargs(
        repository: str = '-home-',     # Default aus der Spec
        metadataset: str = '-default-', # Default aus der Spec
        query: str,                     # <- SyntaxError
    ):

Gemessen gegen edu-sharing 11.0 (Staging, 27.08.2026): ohne diesen Schritt sind
145 von 1131 erzeugten Dateien syntaktisch kaputt, mit ihm null.

Der Default geht dabei nicht verloren -- er ist eine Bequemlichkeit der Web-UI,
und die Komfortschicht setzt ``-home-`` ohnehin selbst.

Aufruf::

    python scripts/generate_client.py                     # gegen die Referenz-Spec
    python scripts/generate_client.py --from-instance URL # gegen eine echte Instanz
"""

from __future__ import annotations

import argparse
import ast
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFERENCE_SPEC = ROOT / "openapi" / "edu-sharing-11.0.json"
OUTPUT = ROOT / "src" / "edusharing" / "_generated"

METHODS = ("get", "post", "put", "delete", "patch")


def fetch_spec(instance_url: str) -> dict:
    """Hole die Spec einer laufenden Instanz. ``swagger.json`` gibt es nicht."""
    url = instance_url.rstrip("/")
    if not url.endswith("/rest"):
        url = f"{url}/rest" if url.endswith("/edu-sharing") else f"{url}/edu-sharing/rest"
    with urllib.request.urlopen(f"{url}/openapi.json", timeout=120) as r:
        return json.load(r)


def strip_path_param_defaults(spec: dict) -> int:
    """Entferne ``schema.default`` von allen Pfad-Parametern. Gibt die Anzahl zurueck."""
    n = 0
    for item in spec.get("paths", {}).values():
        for method, op in item.items():
            if method not in METHODS:
                continue
            for param in op.get("parameters") or []:
                if param.get("in") == "path" and "default" in (param.get("schema") or {}):
                    del param["schema"]["default"]
                    n += 1
    return n


def verify_syntax(root: Path) -> list[str]:
    """Jede erzeugte Datei parsen. Der Generator meldet Syntaxfehler nur als Warnung."""
    broken = []
    for f in root.rglob("*.py"):
        try:
            ast.parse(f.read_text(encoding="utf-8"))
        except SyntaxError as e:
            broken.append(f"{f.relative_to(root)}:{e.lineno}: {e.msg}")
    return broken


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--from-instance", metavar="URL",
                    help="Spec von einer laufenden Instanz holen statt der Referenz-Spec")
    ap.add_argument("--spec", type=Path, default=REFERENCE_SPEC)
    ap.add_argument("--output", type=Path, default=OUTPUT)
    args = ap.parse_args()

    if args.from_instance:
        print(f"hole Spec von {args.from_instance}")
        spec = fetch_spec(args.from_instance)
    else:
        if not args.spec.exists():
            print(f"Referenz-Spec fehlt: {args.spec}", file=sys.stderr)
            print("  -> mit --from-instance URL einmalig erzeugen", file=sys.stderr)
            return 1
        spec = json.loads(args.spec.read_text(encoding="utf-8"))

    info = spec.get("info", {})
    ops = sum(1 for i in spec.get("paths", {}).values() for m in i if m in METHODS)
    print(f"Spec: {info.get('title')} {info.get('version')} "
          f"| {len(spec.get('paths', {}))} Pfade, {ops} Operationen")

    n = strip_path_param_defaults(spec)
    print(f"Pfad-Parameter-Defaults entfernt: {n}")

    tmp = args.output.parent / "_spec-normalisiert.json"
    tmp.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")

    if args.output.exists():
        shutil.rmtree(args.output)
    args.output.mkdir(parents=True, exist_ok=True)

    cmd = [
        "uv", "tool", "run", "--from", "openapi-python-client",
        "openapi-python-client", "generate",
        "--path", str(tmp), "--output-path", str(args.output),
        "--overwrite", "--meta", "none",
    ]
    print("$ " + " ".join(cmd))
    subprocess.run(cmd, check=False)
    tmp.unlink(missing_ok=True)

    broken = verify_syntax(args.output)
    total = sum(1 for _ in args.output.rglob("*.py"))
    if broken:
        print(f"\nFEHLER: {len(broken)} von {total} Dateien syntaktisch kaputt:",
              file=sys.stderr)
        for b in broken[:20]:
            print("   ", b, file=sys.stderr)
        return 1

    print(f"\nOK: {total} Dateien, keine Syntaxfehler.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
