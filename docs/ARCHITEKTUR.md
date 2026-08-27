# edu-sharing Python-Bibliothek — Architektur & Plan

Stand: 27.08.2026 · Status: **Entwurf, zur Freigabe**

Eine Python-Bibliothek, die die REST-API eines edu-sharing-Repositoriums und die
umliegenden Dienste (b-api) so zugänglich macht, dass Dritte sie mit wenig Code
nachnutzen können — **ohne** dass die Bibliothek die Metadaten-Konventionen einer
bestimmten Instanz voraussetzt.

---

## 1. Warum überhaupt

| Was es heute gibt | Warum es nicht reicht |
|---|---|
| `oeh-search-etl/edu_sharing_openapi/` — generierter Client (openapi-generator 7.8.0) | vendored, nicht auf PyPI, synchron, 300+ Modelle, kennt **keine** der gemessenen Fallen. Wer damit schreibt, bekommt `200 OK` und nichts gespeichert. |
| `wlo-mcp-sc` — MCP-Server (TypeScript, ~30 000 Zeilen) | Die faktische Referenzimplementierung der Domänenlogik — aber TypeScript, und die Vokabulare sind für WLO **hartkodiert** (`vocabs.ts`). |
| Rohes `requests`/`httpx` | Jede Anwendung baut die 17 Quirks neu nach — oder fällt auf sie herein. |

**Auf PyPI existiert kein edu-sharing-Client.** Der Namensraum ist frei.

Der Mehrwert dieser Bibliothek ist nicht der HTTP-Zugriff — der ist trivial. Er ist
das **gemessene Verhalten**: welcher Schreibweg für welche Property gilt, dass ein
`200` kein Persistenzbeweis ist, dass es zwei Sammlungs-Suchen gibt und keine die
Obermenge der anderen ist.

## 2. Die zentrale Spannung — und ihre Auflösung

Zwei Anforderungen ziehen gegeneinander:

* **generisch** — andere edu-sharing-Instanzen haben andere Metadatensätze,
  andere Properties, andere Vokabulare. Nichts darf hartkodiert sein.
* **wenig Code** — `repo.search("Photosynthese", fach="Biologie")` statt erst MDS
  laden, dann URIs auflösen, dann Kriterien bauen.

**Auflösung:** Die Vokabular-Auflösung passiert **zur Laufzeit gegen das MDS der
jeweiligen Instanz**, nicht gegen eine eingebaute Tabelle.

```python
repo.vocab.resolve("ccm:taxonid", "Biologie")
# → POST /mds/v1/metadatasets/-home-/{mds}/values   {"pattern": ""}
# → "http://w3id.org/openeduhub/vocabs/discipline/080"
```

Damit funktioniert `fach="Biologie"` auf **jeder** Instanz, die ein Fächer-Vokabular
führt — ohne dass die Bibliothek WLO kennt. Ein WLO-Profil bleibt eine
Bequemlichkeitsschicht obendrauf, keine Voraussetzung.

> Gemessen (Staging, 12.08.2026): `pattern: ""` listet alle Werte —
> das dokumentierte `"-all-"` liefert **leer**. `pattern: "Ph"` ist eine
> funktionierende Präfixsuche, also zugleich ein Typeahead. Der Header
> `locale: en_EN` liefert englische Labels.

## 3. Schichten

```
┌─ 4  Integrationen ──── MCP-Server · Toolschemas · Framework-Adapter
│                        NICHT Teil von v1 — aber v1 muss sie tragen
├─ 3  Agent-Bausteine ── Formatierung · Token-Budget · Confirm · Sanitize · Safety
├─ 2  Ressourcen ─────── repo.search() · node.update() · collection.add()
├─ 1  Profil & MDS ───── Vokabular-Auflösung · Property-Fähigkeiten
├─ 0  Transport ──────── httpx · Auth · Retry · Concurrency · Read-Back · Fehler
└─ _generated ────────── 389 Operationen · 378 Modelle, aus openapi.json
```

Schicht 1 beantwortet auch die Frage, die Dritte nicht beantworten können:
**welcher Schreibweg gilt.** Ist eine Property im MDS → `PUT /metadata`.
Ist sie es nicht → `POST /property`. Die Bibliothek entscheidet das selbst.

## 4. Getroffene Entscheidungen

| # | Entscheidung | Begründung |
|---|---|---|
| E1 | **Volle Endpunkt-Abdeckung** über generierte Schicht | 318 Pfade / 389 Operationen / 378 Schemas; alle mit `operationId` → deterministisch generierbar. Kein toter Winkel. |
| E2 | Generator: **`openapi-python-client`** (Python), nicht der Java-`openapi-generator` | Erzeugt **httpx**-basierte Clients mit async. Der Java-Generator liefert sync/urllib3 — unvereinbar mit E3. Java ist auf der Zielmaschine ohnehin nicht installiert. **Live verifiziert, siehe §4.1.** |
| E3 | **Async-first, Sync-Wrapper** | `AsyncRepository` ist die Wahrheit, `Repository` ein dünner Wrapper (Vorbild: httpx, openai). KI-Anwendungen und Batch-Kuration brauchen Nebenläufigkeit; Notebooks bekommen trotzdem den einfachen Weg. |
| E4 | **Profil-agnostisch von Anfang an** | WLO ist ein mitgeliefertes Profil unter anderen. Etappe 2 wird gegen ein zweites, fremdes Repository verifiziert — sonst zementieren sich WLO-Annahmen (so ist `vocabs.ts` im MCP entstanden). |
| E5 | **Kein MCP-Server in v1** — aber alle Bausteine dafür | Siehe §6. Der MCP wird später *mit* der Bibliothek gebaut, nicht *in* ihr. |
| E6 | Import `edusharing`, Distribution `edu-sharing` | Namensraum auf PyPI frei. *(offen — siehe §9)* |

### 4.1 Machbarkeitsnachweis (27.08.2026, gegen Staging durchgeführt)

E1 und E2 sind **nicht angenommen, sondern gemessen** — mit einem Befund, der die
Pipeline sonst zum Scheitern gebracht hätte:

1. **Der Generator erzeugt aus der unveränderten Spec ungültiges Python.**
   244 Pfad-Parameter tragen einen `schema.default` (`-home-`, `-default-`,
   `-userhome-`); folgt danach ein Parameter ohne Default, entsteht

   ```python
   def _get_kwargs(
       repository: str = '-home-',      # Default aus der Spec
       metadataset: str = '-default-',  # Default aus der Spec
       query: str,                      # ← SyntaxError
   ```

   **145 von 1131 Dateien waren kaputt** (12,8 %) — alle in `api/`, die 701 Modelle
   blieben sauber. Der Generator meldet das nur als Warnung und beendet sich mit
   **Exit-Code 0**. Wer nicht nachprüft, hält das für einen erfolgreichen Lauf.

2. **Ein deterministisches Spec-Preprocessing behebt es vollständig.** Nach dem
   Entfernen der 244 Defaults: **1131 Dateien, 0 Syntaxfehler.** Der Default geht
   nicht verloren — er ist eine Bequemlichkeit der Web-UI, und die Komfortschicht
   setzt `-home-` ohnehin selbst.

3. **Alle 389 Operationen haben eine `asyncio`-Variante.** Deckt sich mit E3.

4. **Live-Aufruf erfolgreich:** `GET /_about` über den generierten async-Client →
   `200`, **edu-sharing 11.0**, 32 Dienste.

Beides — Prüfschritt und Reparatur — steckt in `scripts/generate_client.py`. Das
Script bricht mit Exit-Code 1 ab, wenn auch nur eine Datei nicht parst; die
Syntaxprüfung ist Teil des Generats, nicht optional.

> Einzige verbleibende Warnung: ein `500`-Response ist in der Spec als
> `application/text` deklariert (kein gültiger MIME-Type) und wird ausgelassen.
> Betrifft nur den Fehlerfall eines einzigen Endpunkts.

### Was E1 kostet, und wie wir es begrenzen

Volle Abdeckung heißt Bindung an eine edu-sharing-Version. Gegenmaßnahmen:

1. Generiert wird gegen eine **Referenz-Spec**, die im Repo liegt und versioniert ist.
2. `scripts/generate_client.py` regeneriert gegen **jede** Instanz
   (`GET <repo>/rest/openapi.json`) — wer eine abweichende Version fährt, baut sich
   seine Schicht selbst.
3. Die handgeschriebenen Schichten 0–3 hängen **nur** an den ~30 Operationen, die
   real benutzt werden. Bricht das Generat, bricht nicht die Bibliothek.
4. `repo.raw.get/post(...)` bleibt als Notausgang immer offen.

## 5. Wie es sich anfühlen soll

```python
from edusharing import Repository

repo = Repository.from_env()          # EDU_SHARING_URL / _USER / _PASSWORD
repo = Repository("https://repository.staging.openeduhub.net")   # anonym, nur lesend

# --- Lesen: Labels, keine URIs. Aufgelöst gegen DAS MDS DIESER Instanz.
for hit in repo.search("Photosynthese", fach="Biologie", stufe="Sekundarstufe I"):
    print(hit.title, hit.url)

# --- Schreiben: gemerged, zurückgelesen, wirft bei stillem Drop
node = repo.node("abc-123")
node.update(titel="Neuer Titel", beschreibung="…")
node.keywords.add("Weimar (Ort)")     # Merge, nicht Überschreiben

# --- Sammlungen: beide Such-Legs, weil keines Obermenge des anderen ist
repo.collections.find("Optik")
repo.collection("9e7…").add(node)

# --- Notausgang: jede der 389 Operationen
repo.raw.post("/lti/v13/registration/…", json={...})
```

Der Fehlerfall, der die Bibliothek rechtfertigt:

```
SilentDropError: 'ccm:oeh_collection_compendium_text' wurde nicht gespeichert
  (HTTP 200, nach Read-Back abwesend). Grund: nicht im MDS 'mds_oeh'.
  → node.set_property('ccm:oeh_collection_compendium_text', …) nimmt den Direktweg.
```

b-api im selben Paket, eigener Namensraum:

```python
from edusharing.bapi import BildungsAPI

llm = BildungsAPI.from_env()          # B_API_KEY, X-API-KEY (kein Bearer!)
llm.chat("Fasse zusammen: …")         # wählt Modell nach demand + status
llm.models("academiccloud")           # mit Auslastung
```

## 6. Was ein komplexer MCP später braucht — und deshalb in v1 gehört

Der MCP-Server ist nicht Teil von v1. Die Bausteine, ohne die er später nicht
gebaut werden kann, sind es. Abgeleitet aus `wlo-mcp-sc`:

| Baustein | Warum ein MCP ihn braucht | Vorbild dort |
|---|---|---|
| **Per-Request-Credentials** | Ein Server bedient viele Nutzende — ein globaler Auth-State ist ein Datenleck. Auth muss durch jeden Aufruf durchreichbar sein. | `auth/credential.ts` |
| **Preview-then-confirm** | Der Agent muss zeigen können, *was* er ändern würde, bevor er es tut. Zweiphasiges `ChangeSet`. | `write/confirm.ts`, `write/change-set.ts` |
| **LLM-Formatierung + Token-Budget** | Node → kompakter Text, gekappt, mit URL und nodeId (die ein Modell sonst wegparaphrasiert). | `formatter.ts` (734 Z.), `text-cap.ts` |
| **Prompt-Injection-Entschärfung** | Fremdinhalt aus dem Repositorium landet im Modellkontext. | `text-sanitize.ts` |
| **SSRF-/Private-Host-Schutz** | URLs aus Fremdinhalt werden geholt. | `url-safety.ts` |
| **Strukturierte Ergebnisse statt Exceptions** | Ein Tool gibt Fehler als *Text* zurück; eine Exception beendet den Turn. | `rest/result.ts` |
| **Concurrency + Rate-Limit** | Fan-out über viele Nodes, ohne das Repositorium zu erschlagen. | `concurrency.ts`, `rate-limit.ts` |
| **Auflösungs-Rückmeldung** | „Fach 'Bio' nicht auflösbar — meintest du Biologie?" statt stiller Ergebnisleere. | `vocab-suggest.ts`, `filter-criteria.ts` |
| **Dedupe + Rerank** | Zwei Such-Legs zusammenführen, auf `ccm:original` deduplizieren. | `result-dedupe.ts`, `reranker.ts` |
| **Cache mit TTL** | Vokabular und MDS sind groß und ändern sich selten. | `skill-registry-cache.ts` |

Das ist Schicht 3 (`edusharing.agent`). Sie ist **framework-neutral** — kein MCP-,
kein LangChain-Import. Der MCP-Server ist danach ein dünnes Adapter-Projekt.

## 7. Gemessene Grundlagen, auf denen der Entwurf steht

Nicht vermutet, sondern geprüft (Staging, 27.08.2026, sofern nicht anders vermerkt):

**edu-sharing**

* Referenzinstanz meldet **edu-sharing 11.0** (`GET /_about`), 32 Dienste.
* `GET /rest/openapi.json` → 1,34 MB, OpenAPI 3.0.1, 318 Pfade / 389 Operationen /
  378 Schemas, 36 Familien, **alle mit `operationId`**. `swagger.json` existiert nicht.
  Die größten Familien: ADMIN v1 (61), NODE v1 (53), IAM v1 (47), Assignment v1 (18),
  COLLECTION v1 (16), SEARCH v1 (13), MDS v1 (5).
* `securitySchemes` = `basicAuth` + `cookieAuth`. **Kein Bearer.** Ein Bearer-Header
  wird *ignoriert, nicht abgelehnt* — die Anfrage sieht authentifiziert aus und ist es
  nicht. Der gefährlichste Fehler, den ein Client machen kann.
* Falsche Zugangsdaten geben **401 überall** — kein Rückfall auf „nur öffentlich".
  Ein Tippfehler im Passwort legt jeden Aufruf lahm, statt eingeschränkt zu arbeiten.
* Der MDS ist **17,2 MB** — nie im Anfragepfad. Vokabular kommt aus
  `POST /mds/v1/metadatasets/-home-/{mds}/values`.
* `GET /search/v1/metadata?nodeIds=a&nodeIds=b` **ist kein Batch** — bei zwei IDs
  kommt genau eine zurück. Wer es als Batch nutzt, verliert stillschweigend Knoten.

**b-api** *(Spring Boot, nicht FastAPI — der 404-Trace verrät es)*

* Genau zwei Provider: `academiccloud`, `openai`. Fremde → `400 Provider … not found`.
* `/embeddings`, `/completions` → **403** von Spring Security. Nicht freigegeben.
* Ohne Key → 401. Auth ist `X-API-KEY`, **kein** Bearer.
* `openapi.json`, `/docs`, `/health` liefern HTML (SPA-Fallback) — jede
  Endpunkt-Entdeckung ist Raten. Gehört als bekannte Grenze dokumentiert.
* → „Steuerung der b-api" heißt nicht *Breite abdecken*, sondern **Policy**:
  Modellwahl nach `demand`/`status`, Request-Eigenheiten je Modellfamilie
  (`max_completion_tokens` für GPT-5/o, `enable_thinking:false` für Qwen3 — aber
  **nicht** an Mistral, das gibt 400), Retry auf 429/502/503/504, Semaphore,
  `content or reasoning` beim Auslesen.

Die vollständige Fallensammlung wandert nach `docs/QUIRKS.md`.

## 8. Etappen

| # | Inhalt | Fertig, wenn |
|---|---|---|
| **0** | ~~Generator-Pipeline~~ | ✅ **erledigt** — `scripts/generate_client.py`, verifiziert (§4.1) |
| **1** | Transport, Auth (inkl. Bearer-Falle), Fehlertypen, `_about`-Health, Identitätsprobe | Lesen funktioniert gegen eine beliebige Instanz |
| **2** | MDS-Introspektion, Vokabular-Cache, Label↔URI, Suche mit Facetten, beide Sammlungs-Legs | Läuft gegen ein **Nicht-WLO-Repository** |
| **3** | Nodes, Properties (beide Wege automatisch), Read-Back-Verify, Keywords-Merge, Collections, Dateien | Kuration ohne stille Verluste |
| **4** | `edusharing.agent` (§6) + b-api-Client mit Policy | Ein MCP ließe sich darauf bauen, ohne die Bibliothek zu ändern |

Dokumentation läuft mit, nicht hinterher: **jedes Beispiel in `docs/beispiele/` ist
ein ausführbarer Test gegen Staging.** Was dort nicht läuft, steht nicht im README.

## 9. Offene Punkte

1. **Paketname** — Import `edusharing`, Distribution `edu-sharing`? Alternativen:
   `edusharing-py`, `pyedusharing`.
2. **Sprache der Doku** — README zweisprachig (wie `wlo-mcp-sc`) oder nur Deutsch?
   Docstrings englisch für internationale Nachnutzung?
3. **Zweite Testinstanz** — E4 verlangt ein Nicht-WLO-edu-sharing zum Verifizieren.
   Welches ist erreichbar? (`stable.demo.edu-sharing.net` ist der Default-Host der
   Referenz-Spec — reicht das?)
4. **Lizenz** — in `pyproject.toml` vorläufig **Apache-2.0** gesetzt (wie `wlo-mcp-sc`);
   `LICENSE`-Datei fehlt noch, bis das bestätigt ist.
5. **Schreibtests** — Etappe 3 braucht ein Konto mit Schreibrecht auf Staging und
   einen Ablageort für Wegwerf-Knoten.
