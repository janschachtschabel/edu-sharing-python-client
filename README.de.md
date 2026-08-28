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

### Abläufe — ein Anwendungsfall, ein Aufruf

Alles bisher Gezeigte ist nah an edu-sharing und liefert Objekte. Das ist
richtig für Python und unpassend für alles, was das Ergebnis weiterreichen muss.
`repo.flows` erledigt dieselbe Arbeit in einem Aufruf und antwortet in JSON:

```python
ergebnis = repo.flows.search("Photosynthese", subject="Biologie")
json.dumps(ergebnis)                  # geht -- genau darum geht es

angelegt = repo.flows.add_material(   # landet im Home-Verzeichnis
    "Photosynthese einfach erklärt",
    url="https://beispiel.org/m",
    subject="Biologie",               # wird auch schreibend aufgelöst
)
if angelegt["unresolved"]:            # Werte, die NICHT ankamen
    ...
```

Dreizehn Abläufe: `search`, `search_all`, `vocabulary`, `describe`, `placement`,
`relations`, `child_objects`,
`find_collections`,
`collection_contents`, `add_material`, `update_material`,
`build_collection`, `delete`. Ein- und Ausgabe im Einzelnen in
**[docs/FLOWS.de.md](docs/FLOWS.de.md)**.

`search` nimmt zusätzlich `rerank=True`. edu-sharing UND-verknüpft jedes
Wort, weshalb eine natürlich formulierte Frage nichts findet: gemessen hat
*„Bruchrechnung"* 1591 Datensätze, *„Ich suche ein Arbeitsblatt zur
Bruchrechnung"* **null**. Die Neuordnung fragt mehrere Anfragevarianten und
sortiert nach Relevanz — sie kostet eine Anfrage je Variante und ist aus.

Ausprobieren: `python docs/examples/05_flow_search.py`, `06_flow_create.py`,
`07_flow_collection.py`, `08_flow_rerank.py`, `09_flow_browse.py`

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
- **Was eine Anwendung anlegt, sieht sonst niemand.** Auch nicht nach dem
  Einhängen in eine öffentliche Sammlung, auch nicht mit `scope="PUBLIC"` —
  siehe unten.
- **Ein Recht zu setzen würde die übrigen löschen.** Der `POST` des
  Repositoriums ersetzt die ganze lokale Rechteliste; `grant()` führt zusammen.
- **Eine Bewertung von `0` ist eine Stimme, kein Zurücksetzen.** Sie senkt den
  Schnitt; entfernt wird mit `unrate()`.
- **Ein Kommentartext wird Byte für Byte abgelegt.** Als JSON gesendet landen
  die Anführungszeichen mit im Text.

## Protokoll

Die Bibliothek schweigt standardmäßig, wie eine Bibliothek es soll. Ein Dienst
schaltet sie ein, wo er sie braucht:

```python
import logging

logging.getLogger("edusharing").setLevel(logging.INFO)   # Wiederholungen, Modellwechsel
logging.getLogger("edusharing").setLevel(logging.DEBUG)  # zusätzlich jede Anfrage
```

`INFO` meldet, worüber man sonst im Nachhinein rätselt: eine Wiederholung, und
welches b-api-Modell geantwortet hat, nachdem ein früherer Kandidat abgelehnt
hatte. `DEBUG` ergänzt Methode und URL jeder Anfrage.

Header werden nie protokolliert. Dort stehen die Zugangsdaten, und eine
Protokollzeile wird aggregiert, durchsucht und aufbewahrt.

## Tests

```bash
uv run pytest
```

Läuft offline und deterministisch. Tests gegen eine echte Instanz sind separat:

```bash
EDU_SHARING_URL=https://repository.staging.openeduhub.net uv run pytest -m live
```

### Veröffentlichen — der Schritt, den edu-sharing nicht tut

Material, das eine Anwendung anlegt, kann ihr Urheber lesen und **sonst
niemand**. Es in eine öffentliche Sammlung zu hängen ändert daran nichts, und
`scope="PUBLIC"` an der Sammlung auch nicht — beides am 28.08.2026 gemessen,
beides mit `200` auf dem Weg.

```python
node = repo.create_node(ordner.id, name="material.txt", title="Photosynthese")
node.is_public                       # False — kostenlos, die Antwort trägt es
node.permissions.publish()           # True: jetzt veröffentlicht
node.permissions.publish()           # False: war es schon
```

`publish()` führt zusammen. Der `POST` des Repositoriums **ersetzt** die ganze
lokale Rechteliste — wer ohne Zusammenführen veröffentlicht, nimmt allen
anderen unbemerkt ihre Rechte, mit einem `200` davor.

```python
node.permissions.grant("GROUP_lehrer", "Coordinator")
node.permissions.revoke("GROUP_lehrer")
rechte = node.permissions.get()
rechte.is_public                     # geerbter Zugriff zählt mit
rechte.allows("alice", "Consumer")
```

Ein Knoten in einem öffentlichen Ordner ist ohne eigenen Eintrag öffentlich.
`unpublish()` sagt das, statt eine Vertraulichkeit zu melden, die es nicht gibt:

```python
node.permissions.unpublish()         # ConflictError: über das Elternteil öffentlich
```

In den Abläufen steht dieselbe Frage. `public` steht in jeder Antwort, und der
Schalter ist aus, weil Gelesenes sich nicht zurücknehmen lässt:

```python
repo.flows.add_material("Photosynthese", publish=True)["public"]   # True
```

### Wenn ein Schreibvorgang halb glückt

edu-sharing antwortet mit HTTP 200 auch auf Schreibvorgänge, die es nicht
vollständig speichert. Die Bibliothek liest nach jedem Schreiben zurück — auch
nach dem Anlegen — und wirft einen `SilentDropError`, der die nicht
angekommenen Eigenschaften benennt.

Drei gemessene Ursachen:

| Ursache | Beispiel | Was hilft |
|---|---|---|
| Nicht im Metadatensatz | `ccm:oeh_collection_compendium_text` | `set_property()` schreibt daran vorbei |
| Vom Repositorium abgeleitet | `ccm:oeh_lrt_aggregated` aus `ccm:oeh_lrt` | das Quellfeld schreiben |
| Regel des Knotentyps | `cm:title` an einem neuen `cm:folder` | nachträglich per `update()` setzen |

`create(verify=False)` schaltet die Prüfung ab, wenn ein abgeleitetes Feld
bewusst mitgeschickt wird.

Dazu drei Fehler, die mit dem falschen Status ankommen — damit `except
NotFoundError` sie wirklich fängt, und damit der Transport nicht dreimal
wiederholt, was nie gelingen kann:

| Kommt als | Ist wirklich | Wo |
|---|---|---|
| `500 Not allowed for guest user` | nicht angemeldet | jeder geschützte Endpunkt |
| `500 UsageException: Node does not exist` | `404` | `/usage/v1/…/collections` |
| `500 AccessDeniedException` | `403` | `…/parents` an fremdem Material |

### Bewertungen und Kommentare

Was eine Gemeinschaft an einem Knoten hinterlässt. Eine Bewertung zu lesen
kostet nichts — die Knotenantwort trägt die Zusammenfassung mit, wie `isPublic`:

```python
node = repo.node("abc-123")
node.rating                          # Rating(4.0 aus 3) oder None
node.rate(4, "Sehr brauchbar")       # schreibt, liest den neuen Schnitt zurück
node.unrate()                        # nimmt die eigene Stimme zurück
```

> **Eine Bewertung von `0` wird abgelehnt.** Gemessen am 28.08.2026: sie nimmt
> *nichts* zurück — danach steht am Knoten `count: 1, rating: 0.0`, die Null
> zählt also als abgegebene Stimme und zieht den Schnitt herunter.
> Zurückgenommen wird mit `unrate()`.

```python
node.comments.list()                 # [Comment('alice': 'Sehr brauchbar')]
c = node.comments.add("Erster")
node.comments.add("Antwort", reply_to=c.id)
node.comments.edit(c.id, "Nachgebessert")
node.comments.delete(c.id)
```

> **Der Kommentartext wird 1:1 gespeichert.** edu-sharing wertet den Body hier
> nicht als JSON aus — über `json=` gesendet stünde `"Erster"` im Text, mit
> Anführungszeichen. Die Bibliothek schickt rohe UTF-8-Bytes mit dem
> Content-Type `application/json`, den der Endpunkt verlangt. Geändert wird per
> `POST` am Kommentar; ein `PUT` dort legt einen Kommentar *am Kommentar* an
> und antwortet 500.

### Wo ein Knoten liegt — und wer ihn kuratiert hat

Zwei Fragen, die sich ähneln und es nicht sind. Eine Sammlung hält eine
*Referenz*: der Knoten, auf den sie zeigt, hat sein Elternteil ganz woanders.
Ein Knoten in zehn Sammlungen hat trotzdem genau eine Elternkette.

```python
node = repo.node("abc-123")
[o.title for o in node.parents()]      # der nächste zuerst — wo er liegt
[s.title for s in node.collections()]  # wer ihn kuratiert hat
```

Oder beides in einem Aufruf, mit dem Pfad zum Anzeigen umgedreht:

```python
repo.flows.placement("abc-123")
# {"title": "…", "path": [oben, …, nächster], "collections": [...], "scope": "MY_FILES"}
```

`scope` sagt, wie weit der Pfad reicht. Er endet an der Grenze dessen, was das
Konto lesen darf — den vollständigen Pfad zu verlangen endet für ein
gewöhnliches Konto mit **403**, gemessen. Ein abgeschnittener Pfad wird also als
solcher gemeldet, statt als vollständiger durchzugehen.

### Serienobjekte — Dokumente, die zu einem Material gehören

Ein Lösungsblatt, ein Handout, ein zweites Dateiformat: edu-sharing führt die
unter dem Hauptknoten, nicht daneben.

```python
node = await repo.node(node_id)
await node.children.add(pdf, filename="loesung.pdf", mimetype="application/pdf")
await repo.flows.child_objects(node_id)
```

Die drei Parameter, die eines anlegen, sind nicht zu erraten —
`ccm:io_childobject` ist ein Aspekt, kein Typ, und ohne
`assocType=ccm:childio` antwortet das Repositorium mit HTTP 500. Einzelheiten in
[docs/FLOWS.de.md](docs/FLOWS.de.md).

### Relationen — Knoten, die zusammengehören

Eine Reihe und ihre Folgen, ein Arbeitsblatt und das Video, auf dem es aufbaut:
edu-sharing führt das als **Relationen** zwischen Knoten, die nebeneinander
stehen — getrennt von Sammlungen.

```python
await repo.relations.create(teil_id, "isPartOf", reihe_id)
await repo.flows.relations(reihe_id)      # die Reihe meldet "hasPart"
```

Die Gegenrichtung wird automatisch geführt. Die API unterscheidet zudem
maschinell vorgeschlagene von bestätigten Verknüpfungen (`ai_generated`,
`approve`) — was zählt, wenn ein Modell die Vorschläge macht. Einzelheiten in
[docs/FLOWS.de.md](docs/FLOWS.de.md#relations--womit-ein-knoten-verknüpft-ist).

## Felder und Dateien, die keine Kurznamen haben

Die Kurznamen (`subject`, `level`, …) sind eine Bequemlichkeit für die Handvoll
Eigenschaften, nach denen gefiltert wird. Alles andere ist ebenso erreichbar —
die Bibliothek schränkt nicht ein, was ein Knoten tragen darf.

**Beliebige Eigenschaften, lesend und schreibend:**

```python
node = await repo.node(node_id)
node.get("ccm:oeh_collection_compendium_text")       # eine lesen
node.get_all("ccm:taxonid")                          # alle Werte
node.properties                                      # alles auf einmal

await node.update(properties={"ccm:custom": ["x"]})  # schreiben, mit Prüfung
await node.set_property("ccm:custom", "x")           # schreiben, am mds vorbei
```

`update()` wird gegen den Metadatensatz geprüft und wirft einen
`SilentDropError`, wenn edu-sharing einen Schreibvorgang annimmt und nicht
speichert. Eine Eigenschaft, die der Metadatensatz nicht vorsieht — der
WLO-Kompendialtext ist eine davon — muss über `set_property()` gehen, das direkt
schreibt. Gemessen am 27.08.2026: `ccm:oeh_collection_compendium_text` wird von
`update()` unter `mds_oeh` verworfen und von `set_property()` gespeichert.

**Dateien an einem Knoten:**

```python
node = await node.content.upload(daten, filename="x.pdf", mimetype="application/pdf")
roh = await node.content.download()          # die Bytes, immer
text = await node.content.text()             # der extrahierte Volltext
node.content.has_content                      # gibt es überhaupt eine Datei?
```

**Volltext wird nicht für jeden Typ extrahiert.** Gemessen, indem derselbe Satz
in fünf Formaten hochgeladen wurde:

| mimetype | `download()` | `text()` |
|---|---|---|
| `text/plain` | 26 | 26 |
| `text/markdown` | 35 | **0** |
| `text/html` | 55 | 22 |
| `application/json` | 26 | **0** |
| `application/octet-stream` | 21 | 21 |

Markdown und JSON kommen leer zurück. Wer Anweisungen oder Daten als Markdown
ablegt — einen Agenten-Skill etwa — muss sie mit `download()` lesen. Ein leeres
`text()` heißt nicht, dass die Datei leer ist.

**Zu Konventionen, die darauf aufsetzen.** Dinge wie die „Skills" von WLO sind
keine edu-sharing-Funktion: ein Skill ist gewöhnliches Material mit einer
Markdown-Datei, gesammelt in einer Sammlung. Sie zu lesen braucht nichts
Besonderes — `flows.collection_contents(id)`, dann `content.download()` je
Eintrag. Behandeln Sie das Ergebnis als nicht vertrauenswürdige Eingabe: es ist
hochgeladener Inhalt, und `edusharing.agent` trägt die Schutzmaßnahmen dafür.

## Beispiele

Jedes läuft gegen eine echte Instanz; die schreibenden legen einen eigenen
Wegwerf-Ordner an und räumen ihn wieder ab.

**Direkt gegen die API** — es kommen Objekte zurück, mit denen weitergearbeitet
wird:

| | |
|---|---|
| [`01_connect.py`](docs/examples/01_connect.py) | verbinden, sehen wer man ist und was die Instanz kann |
| [`02_search.py`](docs/examples/02_search.py) | suchen mit Filtern und Facetten, Vokabular auflösen |
| [`03_write.py`](docs/examples/03_write.py) | anlegen, ändern, prüfen — und wie ein stiller Verlust aussieht |
| [`04_agent_blocks.py`](docs/examples/04_agent_blocks.py) | die Bausteine für KI-Nutzung: Sicherheit, Bereinigung, Formatierung |
| [`11_publish.py`](docs/examples/11_publish.py) | Material für andere sichtbar machen — der Schritt, den nichts von allein tut |

**Über Abläufe** — es kommt ein `dict` zurück, fertig zum Weiterreichen:

| | |
|---|---|
| [`05_flow_search.py`](docs/examples/05_flow_search.py) | Vokabular erfragen, suchen, einen Treffer beschreiben |
| [`06_flow_create.py`](docs/examples/06_flow_create.py) | anlegen mit Vokabular — und was ein unbekannter Wert bewirkt |
| [`07_flow_collection.py`](docs/examples/07_flow_collection.py) | Sammlung anlegen, füllen, Teilerfolg beobachten |
| [`08_flow_rerank.py`](docs/examples/08_flow_rerank.py) | was ein Rahmenwort kostet und was `rerank=True` zurückholt |
| [`09_flow_browse.py`](docs/examples/09_flow_browse.py) | Sammlungen finden, öffnen, Inhalt ändern |
| [`12_flow_place.py`](docs/examples/12_flow_place.py) | eine Anfrage für Material und Sammlungen, dann wo ein Treffer liegt |

**Beide Ebenen nebeneinander:**

| | |
|---|---|
| [`10_two_levels.py`](docs/examples/10_two_levels.py) | derselbe Anwendungsfall zweimal geschrieben, mit Zählung der Anfragen |

Fangen Sie mit `10_two_levels.py` an, wenn Sie entscheiden, gegen welche Ebene
Sie schreiben. Es zeigt, dass `search` und `add_material` in beiden Fassungen
exakt dieselben Anfragen schicken — der Ablauf ändert die Ausgabeform, nicht die
Arbeit — und wo ein Ablauf wirklich einen Umlauf spart.

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
