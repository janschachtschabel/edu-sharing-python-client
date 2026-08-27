# edu-sharing für Python

> *English version: [README.md](README.md).*

Python-Bibliothek für [edu-sharing](https://edu-sharing.com)-Repositorien und die
**b-api** (Bildungs-API, OpenEduHub) — **repository-agnostisch** und **async-first**.

> **Status: in Arbeit.** Lesen, Suchen und Schreiben stehen und sind gegen
> edu-sharing 11.0 geprüft — auch schreibend, gegen eine echte Instanz. Offen
> sind die Bausteine für KI-Anwendungen und der b-api-Client; der Fahrplan steht
> in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). Was unten mit ⏳ markiert ist,
> beschreibt das Ziel, nicht den Ist-Stand.

## Warum

edu-sharing hat 318 REST-Pfade und ein Verhalten, das man nicht raten kann: welcher
Schreibweg für welche Property gilt, dass ein `200 OK` **kein** Persistenzbeweis ist,
dass es zwei Sammlungs-Suchen gibt und keine die Obermenge der anderen ist. Diese
Bibliothek kapselt das gemessene Verhalten, damit Dritte es nicht neu herausfinden
müssen.

**Repository-agnostisch** heißt: Vokabulare werden zur Laufzeit gegen den
Metadatensatz *der jeweiligen Instanz* aufgelöst, nicht gegen eine eingebaute
Tabelle. `subject="Biologie"` funktioniert damit auch auf einem Repositorium, das
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
    ergebnis = repo.search("Photosynthese", subject="Biologie", limit=5)

    for offen in ergebnis.unresolved:   # nicht auflösbare Filter — nie stumm
        print("!", offen)               # "ccm:taxonid='Bio' — gemeint: Biologie?"

    for treffer in ergebnis.hits:
        print(treffer.title, treffer.labels("ccm:taxonid"), treffer.url)
```

`subject="Biologie"` wird gegen den Metadatensatz **dieser** Instanz aufgelöst, nicht
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

Zum Ausprobieren: `python docs/examples/01_connect.py` und `02_search.py`

### Schreiben — mit Rückleseprobe

```python
node = repo.node("abc-123")
node = node.update(title="Neuer Titel")     # zurückgelesen, wirft bei stillem Verlust
node = node.add_keywords("Weimar (Ort)")    # ergänzt, ersetzt nicht
node = node.content.upload(daten, filename="material.pdf", mimetype="application/pdf")
```

Warum das nicht trivial ist: **edu-sharing meldet `200 OK` für Schreibvorgänge,
die nicht stattgefunden haben.** Eine Property, die der Metadatensatz nicht
kennt, wird stillschweigend verworfen — Statuscode 200, Wert weg. `update()`
liest deshalb zurück:

```
SilentDropError: Nicht gespeichert: ccm:oeh_collection_compendium_text
  (HTTP 200, nach der Rückleseprobe abwesend oder abweichend). Zwei übliche
  Ursachen: die Property ist im Metadatensatz dieser Instanz nicht vorgesehen,
  oder das Schreibrecht fehlt. node.set_property(...) umgeht die Filterung
  des Metadatensatzes.
```

Auf `set_property` weicht die Bibliothek **nicht** von selbst aus: die Filterung
ist eine Entscheidung des Repositoriums, keine Panne. Sie zu umgehen bleibt ein
bewusster Schritt.

Sammlungen:

```python
sammlung = repo.create_collection("Meine Sammlung")   # privat per Vorgabe
repo.add_to_collection(sammlung.id, node.id)          # Referenz, keine Kopie
```

Zum Ausprobieren: `python docs/examples/03_write.py` — legt einen eigenen
Wegwerf-Ordner an und entfernt ihn wieder.

### Für KI-Anwendungen

`edusharing.agent` ist framework-neutral — kein MCP-, kein LangChain-Import:

```python
from edusharing.agent import as_result, as_untrusted, format_results, is_safe_url

ergebnis = await as_result(                      # Fehler als Ergebnis, nicht als Exception
    repo.search("Photosynthese", subject="Biologie"),
    format=lambda r: format_results(r, max_chars=1500),
)
print(ergebnis.text)                             # id und url überleben jedes Budget

if is_safe_url(hit.source_url):                  # SSRF: URLs aus Fremddaten
    ...
prompt = as_untrusted(hit.description,           # unsichtbare Steuerzeichen raus,
                      label=f"Material {hit.id}")  # als Fremdmaterial gekennzeichnet
```

Und vor dem Schreiben erst zeigen, was passieren würde:

```python
from edusharing.agent import plan_update

plan = await plan_update(node, title="Neuer Titel")
print(plan.describe())        # "cclom:title: 'Alt'  ->  'Neuer Titel'"
if plan.has_changes:
    node = await plan.apply()
```

### Das LLM-Gateway

```python
from edusharing.bapi import BildungsAPI

async with BildungsAPI.from_env() as llm:        # B_API_KEY, X-API-KEY (kein Bearer)
    antwort = await llm.chat("Fasse zusammen: …")
    print(llm.last_model)                        # wessen Antwort war das?
```

Ohne feste Modell-ID wird das am wenigsten ausgelastete bereite Textmodell
gewählt — und bei Bedarf das nächste: `status: ready` heißt nicht, dass ein
Modell antwortet. Die Eigenheiten der Modellfamilien (`max_completion_tokens`
für GPT-5/o, abgeschaltetes Denken bei Qwen3 — aber nicht bei Mistral) stecken
in `bapi.policy`.

Zum Ausprobieren: `python docs/examples/04_agent_blocks.py`

## ⏳ Wohin es geht

Ein MCP-Server als dünner Adapter über `edusharing.agent` — die Bausteine dafür
stehen, der Server selbst ist bewusst nicht Teil der Bibliothek.

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
- **`200 OK` ist kein Persistenzbeweis** beim Schreiben — siehe oben.
- **`downloadUrl` belegt nicht, dass es eine Datei gibt.** Sie ist immer gesetzt;
  ein Knoten ohne Inhalt liefert daran 200 mit null Bytes. `content.has_content`
  prüft den Hash, der auch eine 0-Byte-Datei von *gar keiner* Datei unterscheidet.
- **Schlagworte sind eine geteilte Liste.** `add_keywords` ergänzt; wer
  `cclom:general_keyword` direkt setzt, löscht fremde Einträge.

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
