# edu-sharing für Python

Python-Bibliothek für [edu-sharing](https://edu-sharing.com)-Repositorien und die
**b-api** (Bildungs-API, OpenEduHub) — **repository-agnostisch** und **async-first**.

> **Status: Entwurf.** Es gibt noch keinen lauffähigen Code — nur den Plan
> ([`docs/ARCHITEKTUR.md`](docs/ARCHITEKTUR.md)) und die verifizierte
> Generator-Pipeline. Die Beispiele unten beschreiben das Ziel, nicht den Ist-Stand.

## Warum

edu-sharing hat 318 REST-Pfade und ein Verhalten, das man nicht raten kann: welcher
Schreibweg für welche Property gilt, dass ein `200 OK` **kein** Persistenzbeweis ist,
dass es zwei Sammlungs-Suchen gibt und keine die Obermenge der anderen ist. Diese
Bibliothek kapselt das gemessene Verhalten, damit Dritte es nicht neu herausfinden
müssen.

**Repository-agnostisch** heißt: Vokabulare werden zur Laufzeit gegen den
Metadatensatz *der jeweiligen Instanz* aufgelöst, nicht gegen eine eingebaute
Tabelle. `fach="Biologie"` funktioniert damit auch auf einem Repositorium, das
nichts mit WirLernenOnline zu tun hat.

## So soll es aussehen

```python
from edusharing import Repository

repo = Repository.from_env()

for hit in repo.search("Photosynthese", fach="Biologie", stufe="Sekundarstufe I"):
    print(hit.title, hit.url)

node = repo.node("abc-123")
node.update(titel="Neuer Titel")      # gemerged, zurückgelesen, wirft bei stillem Drop
node.keywords.add("Weimar (Ort)")     # Merge statt Überschreiben
```

Und das LLM-Gateway:

```python
from edusharing.bapi import BildungsAPI

llm = BildungsAPI.from_env()
llm.chat("Fasse zusammen: …")         # wählt das Modell nach Auslastung
```

## Aufbau

| Schicht | Inhalt |
|---|---|
| `edusharing.agent` | Bausteine für KI-Anwendungen: Formatierung, Token-Budget, Preview-then-confirm, Sanitisierung |
| `edusharing` (Ressourcen) | `search()`, `node()`, `collection()` — die intuitive Oberfläche |
| Profil & MDS | Vokabular-Auflösung, Property-Fähigkeiten, Wahl des Schreibwegs |
| Transport | httpx, Auth, Retry, Concurrency, Read-Back-Verify |
| `_generated` | alle 389 Operationen, aus `openapi.json` erzeugt |

## Generierte Schicht neu bauen

```bash
python scripts/generate_client.py --from-instance https://repository.staging.openeduhub.net
```

Die Referenz-Spec (edu-sharing 11.0) liegt unter `openapi/`. Das Script normalisiert
sie zuerst — ohne diesen Schritt erzeugt der Generator ungültiges Python; die
Begründung steht im Docstring des Scripts.

## Lizenz

Apache-2.0
