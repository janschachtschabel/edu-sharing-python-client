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
import hashlib
import json
import shutil
import subprocess
import sys
import tomllib
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


def generator_version() -> str:
    """Welche Fassung des Generators uv.lock festhaelt."""
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    for paket in lock.get("package", []):
        if paket.get("name") == "openapi-python-client":
            return str(paket.get("version") or "unbekannt")
    return "unbekannt"


def write_provenance(output: Path, spec_bytes: bytes, quelle: str, info: dict) -> None:
    """Woraus diese Schicht entstanden ist -- neben die Schicht geschrieben.

    Ohne diese Notiz stand in ``_generated/`` nirgends, welcher Generator und
    welche Spec die eingecheckten Dateien erzeugt haben. Wer spaeter neu
    erzeugt, bekommt dann einen Diff, in dem sich Spec-Aenderung und
    Generator-Aenderung nicht trennen lassen (Audit DEP-2).
    """
    (output / "GENERATED.md").write_text(
        "# Herkunft dieser Schicht\n\n"
        "Maschinenausgabe. Nicht von Hand aendern -- `scripts/generate_client.py`\n"
        "schreibt sie samt dieser Notiz neu.\n\n"
        f"- Generator: `openapi-python-client` {generator_version()} (aus `uv.lock`)\n"
        f"- Spec: {info.get('title')} {info.get('version')}\n"
        f"- Quelle: `{quelle}`\n"
        f"- SHA-256 der Spec: `{hashlib.sha256(spec_bytes).hexdigest()}`\n\n"
        "Der Hash gilt fuer die Spec, wie sie gelesen wurde -- vor dem Entfernen\n"
        "der Pfad-Parameter-Defaults, das das Skript deterministisch vornimmt.\n",
        encoding="utf-8")


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
        spec_bytes = json.dumps(spec, ensure_ascii=False, sort_keys=True).encode("utf-8")
    else:
        if not args.spec.exists():
            print(f"Referenz-Spec fehlt: {args.spec}", file=sys.stderr)
            print("  -> mit --from-instance URL einmalig erzeugen", file=sys.stderr)
            return 1
        spec_bytes = args.spec.read_bytes()
        spec = json.loads(spec_bytes.decode("utf-8"))

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

    # ``uv run`` statt ``uv tool run``: so kommt der Generator aus uv.lock und
    # nicht die neueste Fassung von PyPI. Eine 141k-Zeilen-Schicht, deren Bau
    # sich nicht wiederholen laesst, ist ein Blob auf Zuruf -- und ein
    # unfreiwilliges Update des Generators ergaebe einen Diff, in dem niemand
    # Spec-Aenderung von Generator-Aenderung trennen kann (Audit DEP-2).
    #
    # ``cwd=ROOT`` ist keine Formsache. Gemessen am 08.09.2026: laeuft der
    # Generator im Projekt, liest er pyproject.toml -- ``requires-python
    # >=3.11`` laesst ihn ``typing.Self`` schreiben statt
    # ``typing_extensions.Self`` (weshalb typing-extensions keine
    # Abhaengigkeit ist, Audit DEP-1), und ``line-length = 100`` bestimmt die
    # Formatierung. Ausserhalb des Projekts erzeugt derselbe Generator aus
    # derselben Spec 556 andere Dateien -- gleicher Inhalt, andere Form.
    cmd = [
        "uv", "run", "openapi-python-client", "generate",
        "--path", str(tmp), "--output-path", str(args.output),
        "--overwrite", "--meta", "none",
    ]
    print("$ " + " ".join(cmd))
    lauf = subprocess.run(cmd, check=False, cwd=ROOT)
    tmp.unlink(missing_ok=True)
    if lauf.returncode != 0:
        # Der Rueckgabewert wurde bisher verworfen. Ein gescheiterter Generator
        # hinterliess damit einen halben Baum und meldete Erfolg.
        print(f"\nFEHLER: der Generator endete mit {lauf.returncode}.",
              file=sys.stderr)
        return 1

    broken = verify_syntax(args.output)
    total = sum(1 for _ in args.output.rglob("*.py"))
    if broken:
        print(f"\nFEHLER: {len(broken)} von {total} Dateien syntaktisch kaputt:",
              file=sys.stderr)
        for b in broken[:20]:
            print("   ", b, file=sys.stderr)
        return 1

    # posix: die Notiz wird eingecheckt und darf nicht nach Windows aussehen.
    quelle = args.from_instance or args.spec.relative_to(ROOT).as_posix()
    write_provenance(args.output, spec_bytes, quelle, info)
    print(f"\nOK: {total} Dateien, keine Syntaxfehler.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
