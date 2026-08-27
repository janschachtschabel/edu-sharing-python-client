# edu-sharing für Python

Python-Bibliothek für [edu-sharing](https://edu-sharing.com)-Repositorien und die
**b-api** (Bildungs-API, OpenEduHub) — **repository-agnostisch** und **async-first**.

> **Status: in Arbeit.** Verbinden, Suche, Vokabular und Sammlungen stehen und
> sind gegen edu-sharing 11.0 geprüft. Schreibzugriff folgt — der Fahrplan steht
> in [`docs/ARCHITEKTUR.md`](docs/ARCHITEKTUR.md). Was unten mit ⏳ markiert ist,
> beschreibt das Ziel, nicht den Ist-Stand.

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

## Was heute geht

```python
from edusharing import Repository

with Repository("https://repository.staging.openeduhub.net") as repo:
    about = repo.about()
    print(about.repository_version)   # 11.0
    print(about.plugins)              # ['mongo-plugin', 'b-api', ...]

    wer = repo.whoami()               # als wer laufe ich hier?
    print(wer.authority)              # 'esguest' = anonym
```

`AsyncRepository` ist dieselbe Oberfläche für asynchronen Code; der synchrone
Zugang funktioniert auch im Notebook, wo bereits ein Event-Loop läuft.

Zugangsdaten kommen aus der Umgebung (`EDU_SHARING_URL`, `EDU_SHARING_USER`,
`EDU_SHARING_PASSWORD`) oder direkt:

```python
repo = Repository(url, auth=("benutzer", "passwort"))
```

Jeder der 389 Endpunkte ist erreichbar, auch ohne eigene Methode:

```python
werte = await repo.raw.json("GET", "/config/v1/values")
```

### Suchen mit Labels statt URIs

```python
with Repository(url, metadataset="mds_oeh") as repo:
    ergebnis = repo.search("Photosynthese", fach="Biologie", limit=5)

    for offen in ergebnis.unresolved:   # nicht auflösbare Filter — nie stumm
        print("!", offen)               # "ccm:taxonid='Bio' — gemeint: Biologie?"

    for treffer in ergebnis.hits:
        print(treffer.title, treffer.labels("ccm:taxonid"), treffer.url)
```

`fach="Biologie"` wird gegen den Metadatensatz **dieser** Instanz aufgelöst, nicht
gegen eine eingebaute Tabelle. Welche Metadatensätze es gibt, sagt
`repo.metadatasets()`; die Wahl ändert, was filterbar ist und was gefunden wird.

Facetten zählen serverseitig über die ganze Ergebnismenge:

```python
ergebnis = repo.search("Photosynthese", facets=["ccm:educationalcontext"])
for wert in ergebnis.facets[0].values:
    print(wert.count, wert.value)
```

### Sammlungen

```python
repo.find_collections("Optik")
```

Fragt **beide** Sammlungs-Suchen von edu-sharing gleichzeitig ab und führt sie
zusammen — keine ist Obermenge der anderen. Bei „Deutsch" ist ihre Schnittmenge
gemessen **null**.

Zum Ausprobieren: `python docs/beispiele/01_verbinden.py` und `02_suchen.py`

## ⏳ Wohin es geht

```python
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

## Was die Bibliothek für dich weiß

Ein paar Verhaltensweisen von edu-sharing kann man nicht raten. Sie sind hier
eincodiert statt dokumentiert:

- **Ein Bearer-Token wird abgelehnt, nicht gesendet.** edu-sharing kennt nur
  Basic-Auth und Session-Cookies — und *ignoriert* einen Bearer-Header, statt
  ihn abzulehnen. Die Anfrage liefe unbemerkt als Gast.
- **HTTP 500 heißt manchmal „nicht angemeldet".** Ein Gast auf einem
  geschützten Endpunkt bekommt 500 mit „Not allowed for guest user". Das wird
  zu `AuthenticationError` — und nicht wiederholt.
- **Das Passwort geht nur an das konfigurierte Repositorium.** Auch dann, wenn
  eine URL aus Antwortdaten woandershin zeigt.
- **Ein Vokabular zu haben heißt nicht, danach filtern zu können.**
  `ccm:taxonid` führt in beiden geprüften Metadatensätzen ein Vokabular, ist aber
  nur in `mds_oeh` filterbar. Trifft die Suche darauf, ergänzt die Bibliothek die
  Servermeldung um den fehlenden Hinweis.
- **`pattern:""` listet alle Vokabularwerte** — das naheliegende `"-all-"` gibt
  lautlos eine leere Liste zurück.
- **Nicht auflösbare Filter werden gemeldet, nicht verworfen.** Eine
  fallengelassene Einschränkung liefert Treffer, die niemand angefragt hat, und
  sieht dabei wie ein Ergebnis aus.

## Tests

```bash
uv run pytest
```

Läuft offline und deterministisch. Tests gegen eine echte Instanz sind separat:

```bash
EDU_SHARING_URL=https://repository.staging.openeduhub.net uv run pytest -m live
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
