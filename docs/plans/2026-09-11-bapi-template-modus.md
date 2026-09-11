# Design: Der Template-Modus der B-API

## Ziel

Die Bibliothek kann den zweiten Betriebsmodus der B-API benutzen — serverseitige
Prompt-Templates unter `/api/v1/edu-sharing/*` —, und zwar **unabhängig** vom
Proxy-Modus und **ohne jeden Nachteil** für ihn.

## Kontext

Die B-API hat zwei Modi. Den Proxy (`/api/v1/llm/{provider}/…`, OpenAI-kompatibel)
bedient `BildungsAPI` seit August. Den Template-Modus kennt die Bibliothek nicht:
dort liegen die Prompts serverseitig im Metadatenset, der Client schickt nur
Konfigurations-IDs, einen Kontext-Knoten und Werte. Gemessen am 11.09.2026:

| Befund | Quelle |
|---|---|
| Endpunkte `chat/completion`, `images/generations`, `responses` (je auch `/limited`), `suggestions`, `qas` | `/v3/api-docs` |
| 22 Live-Konfigurationen in `mds_oeh.aiConfigs` und `widgets[].aiConfigs`; Syntax `{{var(X)\|node(X)\|-}}`, `widget(...)` | Metadatenset auf Staging |
| **Alle fünf Felder Pflicht**: `metadataSet`, `configIds`, `user`, `contextNodeId`, `variables` (auch `{}`) | Probe, je 400 |
| `/limited` nimmt nur `[{widgetId, valueId}]`; eine Map scheitert beim Deserialisieren | Probe, 400 |
| Unbekannte Config-ID → **500** `Missing MDS AI configuration for id …` | Probe |
| Fehlerkörper `{error, message, path, status, timestamp, trace}` — `trace` ist ein Java-Stacktrace von ~18 KB | Probe |
| `var()` gewinnt vor `node()`, je Ausdruck; Config-Kette setzt Provider, Modell und Nachricht zusammen; Antwort ist OpenAI `chat.completion` | zwei echte Aufrufe |
| `/suggestions` legt edu-sharing-Vorschläge an (`SuggestionResponseDTO`) — dieselben Felder, die `Suggestion.from_response` liest | Spec |

## Umfang

Drin:
- eine Klasse `BapiTemplates` mit `chat`, `chat_limited`, `respond`,
  `respond_limited`, `images`, `images_limited`, `suggest`, `qas`
- ein Wert `NodeConfig` für Konfigurationen, die auf einem Knoten liegen
- README (beide Sprachen), REFERENCE (beide), Skill (beide), CHANGELOG, ein
  Beispiel `22_bapi_templates.py`, Offline- und Live-Tests
- die Korrektur des `client.py`-Docstrings: `/v3/api-docs` beschreibt die
  Proxy-Routen in eigenen Gruppen (`/v3/api-docs/openai`, `…/academiccloud`),
  und seine „handgeschriebenen Controller" sind genau der Template-Modus

Nicht drin:
- **eine blockierende Fassade.** `BildungsAPI` hat keine; der Template-Modus
  bekommt dieselbe Form. Beide zusammen blockierend zu machen ist ein eigener
  Schritt.
- **ein Zugang von `BildungsAPI` aus** (`api.templates`). Er würde die beiden
  koppeln, ohne etwas zu ermöglichen, das nicht schon geht: einen gemeinsamen
  Verbindungspool bekommt, wer beiden denselben `client=` gibt — die Konvention
  der Bibliothek.
- Konfigurationen schreiben (`ccm:bapi_config` auf Knoten anlegen) — der Modus
  liest sie, er verwaltet sie nicht.
- ein typisierter QA-Wert: `/qas` ist laut Spec **EXPERIMENTAL**, das Schema kann
  sich ändern. Ein Typ darüber müsste mitwandern; ein `dict` nicht.

## Ansatz

**Gewählt: eine eigenständige Klasse mit eigenem Anfrageweg, gebaut aus den
geteilten Bausteinen.**

| | Wie | Dafür | Dagegen |
|---|---|---|---|
| A · Methoden an `BildungsAPI` | `api.template_chat(...)` | ein Objekt | `client.py` hat 614 Zeilen; der Proxy wächst um eine zweite Verantwortung; jede Änderung am Template-Modus fasst die Proxy-Klasse an |
| B · eigene Klasse, **leiht** sich `BildungsAPI._request` | wie `passthrough` es tut | kein doppelter Anfrageweg | `_request` wiederholt **500** — gemessen der Code für eine falsche Config-ID —, und es wiederholt jeden POST, auch einen, der schon Vorschläge angelegt hat |
| **C · eigene Klasse, eigener Anfrageweg aus `RetryPolicy`, `error_class_for`, `redirect_error`, `non_json_error`** | `bapi/templates.py` | andere Fehler- und Wiederholungsregeln, ohne den Proxy anzufassen | die Schleife steht zweimal (je ~40 Zeilen) |

C, weil die beiden Anfragewege **verschiedene Regeln** brauchen. Das ist dieselbe
Begründung, mit der `client.py` schon den edu-sharing-`Transport` nicht
mitbenutzt: „Parameterising it for both would have made each side less clear."
Was sich teilen lässt, wird geteilt: Wiederholungspolitik, Fehlerklassen,
Weiterleitungs- und JSON-Fehler, die Adressprüfung, und die **Antwort-Parser**
des Proxys.

## Globale Randbedingungen

- Python ≥ 3.11, keine neue Abhängigkeit, `mypy --strict`, `ruff`.
- Code, Docstrings und README englisch; Pläne und Testnamen deutsch (Konvention).
- Jede öffentliche Zusage bekommt einen Test; jede Wache wird durch Mutation belegt.
- Geheimnisse nur aus der Umgebung, nie in Meldungen; `refuse_userinfo` für die Adresse.

## Architektur

### Dateien

| Datei | Verantwortung |
|---|---|
| `src/edusharing/bapi/templates.py` (neu, 500 Z., davon gut die Hälfte Docstrings) | `BapiTemplates`, Anfrageweg, Fehlerabbildung |
| `src/edusharing/bapi/template_body.py` (neu, 128 Z.) | `NodeConfig`, `Config`, `Values`, `DEFAULT_USER`; Form der Anfrage, Liste der schreibenden Routen — geteilt wie `body.py`/`client.py` |
| `src/edusharing/bapi/passthrough.py` | zwei reine Parser herausgezogen: `_answer_from`, `_images_from` — sonst unverändert |
| `src/edusharing/bapi/__init__.py` | Export `BapiTemplates`, `NodeConfig` |
| `src/edusharing/bapi/client.py` | nur der Docstring zu `/v3/api-docs` |
| `tests/test_bapi_templates.py` (neu) | offline, `httpx.MockTransport` |
| `tests/test_live_bapi_templates.py` (neu) | live gegen Staging; `suggest` unter `-m write` |
| `tests/test_bapi_client.py` | eine Wache: die öffentliche Fläche von `BildungsAPI` ist gepinnt |
| `docs/examples/22_bapi_templates.py` (neu) | lesendes Beispiel |
| README, REFERENCE, Skill (je zwei Sprachen), CHANGELOG | Doku |

### Datenfluss

```
BapiTemplates.chat(configs, context_node_id=…, user=…, variables=…)
  ├─ _template_body(): configs → [{"type":"mds","id":…} | {"type":"node",…}]
  │           variables → {key: [str, …]}      (limited: choices → [{widgetId, valueId}])
  │           prüft vor dem Senden: configs nicht leer, context_node_id und user gesetzt
  ├─ _post("/api/v1/edu-sharing/chat/completion", body, writes=False)
  │     X-API-KEY, RetryPolicy, Semaphore; Fehler aus "message", nie aus "trace"
  └─ read_answer(antwort)  → str          (derselbe Parser wie BildungsAPI.chat)
```

### Schnittstellen

```python
@dataclass(frozen=True)
class NodeConfig:
    node_id: str
    config_name: str

Config = str | NodeConfig            # str = MDS-Konfiguration, die häufige Form
Values = Mapping[str, str | Sequence[str]]

class BapiTemplates:
    def __init__(self, api_key: str, *, base_url: str, metadataset: str,
                 timeout: float | None = None, max_retries: int = 3,
                 max_concurrency: int = 6, backoff_base: float = 2.5,
                 client: httpx.AsyncClient | None = None) -> None
    @classmethod
    def from_env(cls, **kwargs) -> BapiTemplates    # B_API_KEY, B_API_BASE_URL, EDU_SHARING_METADATASET

    async def chat(self, configs, *, context_node_id, user="guest", variables=None) -> str
    async def chat_limited(self, configs, *, context_node_id, user="guest", choices) -> str
    async def respond(self, configs, *, context_node_id, user="guest", variables=None) -> Answer
    async def respond_limited(self, configs, *, context_node_id, user="guest", choices) -> Answer
    async def images(self, configs, *, context_node_id, user="guest", variables=None) -> list[GeneratedImage]
    async def images_limited(self, configs, *, context_node_id, user="guest", choices) -> list[GeneratedImage]
    async def suggest(self, configs, widgets: Mapping[str, str], *, context_node_id,
                      user="guest", variables=None) -> list[Suggestion]
    async def qas(self, node_ids: Sequence[str]) -> list[dict[str, Any]]
    async def aclose(self) -> None      # plus async with
```

**Entscheidungen im Einzelnen:**
- `variables` (frei) und `choices` (Wert-IDs) heißen verschieden, damit der
  Unterschied zwischen Normal- und Limited-Modus im Aufruf steht und nicht nur
  im Pfad. Beide nehmen dieselbe Form `{schlüssel: wert | [werte]}`; ein
  einzelner String wird zur Liste — der Server erwartet Listen.
- `user="guest"`: der Server verlangt das Feld für `user(...)`-Platzhalter;
  gemessen nutzt keine der 22 Konfigurationen einen. `"guest"` hat in den Proben
  funktioniert und trägt keine Personendaten.
- `metadataset` ist Pflicht, ohne Vorgabe: dort liegen die Konfigurationen, und
  die Bibliothek ist repositoriumsunabhängig — ein erratenes `mds_oeh` wäre
  WLO-spezifisch. `from_env` nimmt `EDU_SHARING_METADATASET`, die Variable, die
  `Repository` schon liest.
- `widgets={"ccm:…": "default"}`: `{widgetId: aiConfigId}`. Gemessen tragen alle
  elf Widget-Konfigurationen die ID `default`.

### Fehler und Wiederholungen

| Lage | Verhalten |
|---|---|
| leere `configs`, fehlende `context_node_id`, leerer `user` | `ValidationError` **vor** dem Senden — der Server wüsste es auch, aber seine Meldung nennt das Feld erst nach 150 Zeichen Java-Klassenname |
| 400 | `ValidationError`, Text aus `message` |
| 500 `Missing MDS AI configuration for id X` | `ValidationError` „das Metadatenset hat keine KI-Konfiguration X" — **nicht wiederholt** |
| jede andere 500 | Fehler, **nicht wiederholt**: gemessen trägt 500 Konfigurationsfehler |
| 429, 502, 503, 504 bei `chat`/`respond`/`images` (+ limited) | wiederholt nach `RetryPolicy` — ein zweiter Versuch kostet Tokens, schreibt aber nichts |
| 429, 503 bei `suggest`/`qas` | wiederholt: abgewiesen, bevor etwas geschah |
| 502, 504 bei `suggest`/`qas` | **nicht wiederholt**, Meldung sagt: „möglicherweise schon angelegt, prüfen statt wiederholen" |
| `trace` im Fehlerkörper | wird **nie** in eine Meldung übernommen |

### Abhängigkeiten

Keine neuen. `templates.py` importiert nur, was `client.py` schon importiert.

## Nicht-funktional

- **Leistung / kein Nachteil für den Proxy:** der Proxy-Anfrageweg bleibt Byte
  für Byte, wie er ist; `passthrough` bekommt zwei herausgezogene Funktionen,
  verhaltensgleich. Gemessen wird: Importzeit von `edusharing.bapi` vorher/nachher.
- **Sicherheit:** im Normalmodus landet `variables` wörtlich im Prompt — gemessen
  hat ein Variablenwert die ganze Antwort umgelenkt. Die Doku sagt: für Eingaben,
  denen man nicht traut, `*_limited`. Die Adresse geht durch `refuse_userinfo`,
  der Schlüssel nie in eine Meldung, der Stacktrace nie in eine Ausnahme.
- **Beobachtbarkeit:** wie der Proxy — eine Ausnahme mit Status und URL.

## Risiken

| Risiko | Gegenmittel |
|---|---|
| Die Extraktion in `passthrough` ändert Proxy-Verhalten | eigener erster Commit; die unveränderten Proxy-Tests vorher und nachher grün |
| `BildungsAPI` wächst versehentlich | Wache pinnt seine öffentlichen Namen |
| Die Fehlertexte der B-API ändern sich (`Missing MDS AI configuration`) | Rückfall ist ein generischer, nicht wiederholter Fehler — sicher, nur weniger freundlich |
| `/qas`-Schema ändert sich | Rückgabe ist `dict`, kein Typ |
| Live-Configs auf Staging ändern sich | Live-Tests lesen die Kette aus dem Metadatenset statt sie zu raten, und überspringen, wenn sie fehlt |

## Offene Fragen

Keine. Die fünf Stellen, an denen man anders entscheiden könnte, stehen oben unter
„Entscheidungen im Einzelnen" und „Nicht drin".

---

## Aufgaben

### Phase 1 — Grundlage, ohne den Proxy zu verändern

**Schritt 0: `/better-coding-workflow` laden.**

**Aufgabe 1 · Parser herausziehen (Refactor, Proxy verhaltensgleich)**
- Ändern: `src/edusharing/bapi/passthrough.py` — `_answer_from(body, model) -> Answer`
  und `_images_from(body) -> list[GeneratedImage]`; `respond()` und `images()`
  rufen sie.
- Beleg: `tests/test_bapi_passthrough.py` unverändert grün, vorher und nachher;
  keine Testdatei des Proxys wird angefasst.
- Commit: `refactor: die Antwort-Parser des Proxys stehen fuer sich`

**Aufgabe 2 · Wache: die Fläche von `BildungsAPI` ist gepinnt**
- Test in `tests/test_bapi_client.py`: `{n for n in dir(BildungsAPI) if not n.startswith("_")}`
  gleich der heute gemessenen Menge. Grün vor jeder Änderung, damit sie beweist,
  dass der Proxy nichts gewinnt und nichts verliert.
- Mutation: ein Name in der Menge vertauscht → rot.

### Phase 2 — Der Template-Modus

**Schritt 0: `/better-coding-workflow` neu laden.**

**Aufgabe 3 · Kleinste durchgehende Scheibe: `chat`**
- Test zuerst (`tests/test_bapi_templates.py`): der gesendete Körper hat genau die
  fünf Felder; `"a"` → `{"type":"mds","id":"a"}`; `NodeConfig("n","c")` →
  `{"type":"node","nodeId":"n","configName":"c"}`; `variables={"k":"v"}` →
  `{"k":["v"]}`; ohne Variablen `{}`; Pfad `/api/v1/edu-sharing/chat/completion`;
  Kopf `X-API-KEY`; Rückgabe ist der Text aus `choices[0].message.content`.
- Umsetzung: `templates.py` mit `NodeConfig`, `BapiTemplates.__init__`, `_body`,
  `_post`, `chat`.

**Aufgabe 4 · Prüfung vor dem Senden**
- Tests: leere `configs`, leere `context_node_id`, leerer `user`,
  Variablenwert kein String → `ValidationError`, **kein** Request (MockTransport
  zählt null Aufrufe).

**Aufgabe 5 · Fehler und Wiederholungen**
- Tests: 400 → `ValidationError` mit `message`; 500 „Missing MDS AI configuration
  for id x" → `ValidationError`, genau **ein** Aufruf; andere 500 → Fehler, ein
  Aufruf; 503 bei `chat` → wiederholt, zweiter Versuch gelingt; `trace` taucht
  in `str(fehler)` nie auf (Probe-String im trace).

**Aufgabe 6 · `chat_limited`**
- Tests: `choices={"w":"v"}` → `[{"widgetId":"w","valueId":"v"}]`; mehrere Werte →
  mehrere Paare; Pfad `…/chat/completion/limited`; `variables` gibt es hier nicht.

**Aufgabe 7 · `respond`, `respond_limited`, `images`, `images_limited`**
- Tests: Pfade; `respond` → `Answer` (über `_answer_from`); `images` →
  `list[GeneratedImage]` (über `_images_from`).

**Aufgabe 8 · `suggest`**
- Tests: `widgets={"w":"default"}` → `widgetAiConfigs=[{"widgetId":"w","aiConfigId":"default"}]`;
  Rückgabe `list[Suggestion]`; 504 → **nicht** wiederholt, Meldung nennt „möglicherweise
  angelegt"; 503 → wiederholt.

**Aufgabe 9 · `qas`**
- Tests: Körper `{"nodeIds":[…]}`, leere Liste → `ValidationError`; Rückgabe
  `list[dict]`; 504 nicht wiederholt.

**Aufgabe 10 · Lebenszyklus und Umgebung**
- Tests: `from_env` braucht Schlüssel, Adresse, Metadatenset — je eigener Fehler;
  `refuse_userinfo` auf der Adresse; ein mitgebrachter `client` wird nicht
  geschlossen; `async with` schließt den eigenen.

**Aufgabe 11 · Export**
- `bapi/__init__.py`: `BapiTemplates`, `NodeConfig`. `test_docs_complete` wird
  rot, bis REFERENCE sie nennt — das treibt Phase 3.

### Phase 3 — Doku, Beispiel, Live

**Schritt 0: `/better-coding-workflow` neu laden.**

**Aufgabe 12 · REFERENCE (beide Sprachen)** — Tabelle je Methode, `NodeConfig`,
die Fehlertabelle kurz; `test_docs_complete` wieder grün.

**Aufgabe 13 · README (beide Sprachen)** — Abschnitt „The template mode" hinter
„The LLM gateway": was er ist, ein Beispiel, wann welcher Modus, `/limited` und
die Prompt-Injection-Notiz, der Anschluss an `node.suggestions`.

**Aufgabe 14 · `client.py`-Docstring** — `/v3/api-docs`-Aussage berichtigen.

**Aufgabe 15 · Beispiel `22_bapi_templates.py`** — lesend: die echte Kette,
dieselbe mit `var` statt `node`, einmal limited. Überspringt ohne `B_API_*`.

**Aufgabe 16 · Skill (beide Sprachen)** — Tabellenzeile, Beispielbereich `01…22`.

**Aufgabe 17 · Live-Tests** — `-m live`: die Kette, `var` vor `node`, limited,
Prüfung vor dem Senden, unbekannte Config. `-m write`: `suggest` an einem
Wegwerf-Knoten, zurückgelesen über `repo.node(…).suggestions.list()`, danach
gelöscht.

**Aufgabe 18 · CHANGELOG** — `[Unreleased]`/Added.

## Verifikation

| Anforderung | Beleg | Fehlerbild |
|---|---|---|
| Template-Modus nutzbar | Offline-Tests je Methode; Live: Kette antwortet, `var` vor `node` | ein Test rot |
| Unabhängig vom Proxy | `BapiTemplates` baut und arbeitet ohne `BildungsAPI`-Instanz; Beispiel benutzt nur ihn | Import oder Konstruktion verlangt `BildungsAPI` |
| **Kein Nachteil für den Proxy** | alle Proxy-Tests unverändert grün; Fläche von `BildungsAPI` gepinnt; Importzeit gemessen | ein Proxy-Test rot, neuer Name an `BildungsAPI`, Importzeit spürbar höher |
| Keine Doppel-Anlage | Test: `suggest` nach 504 genau ein Aufruf | zwei Aufrufe |
| Kein Stacktrace in Meldungen | Test mit Probe-String im `trace` | String in `str(fehler)` |
| Doku stimmt | `test_docs_complete`, `test_docs_code`, Live-Beispiel | Wache rot |

Regression: die ganze Suite, `ruff`, `mypy --strict`, die Live-Suiten `-m live` und
`-m write` gegen Staging.

## Umsetzung — Abweichungen und Befunde (11.09.2026)

**Abweichungen vom Plan**

- `templates.py` wurde nach der Umsetzung geteilt: die Form der Anfrage steht in
  `template_body.py`, wie beim Proxy `body.py` neben `client.py`. Die 61 Tests
  blieben dabei unverändert grün.
- `choices` hat die Vorgabe `None` (sendet `[]`) — wie `variables`; harmlos.
- Der Schalter heißt `writes`, nicht `persists`.
- `test_docs_code` prüft jetzt auch Codeblöcke mit `templates` gegen die echte
  Klasse; die Aussage zu `/v3/api-docs` stand auch im Kopf von
  `tests/test_bapi_passthrough.py` und wurde dort mit berichtigt (nur Text).

**Befunde der Live-Messung, die der Plan nicht kannte** — alle in Docstrings,
REFERENCE und Live-Tests festgehalten:

- Das Gateway liest den Kontext-Knoten mit **seinem eigenen Konto**: ein privater
  Knoten antwortet 403, auch mit dem Eigentümer als `user`. Vorschläge legt es
  unter `admin@B-API` an. Eine 403 sagt das jetzt in der Meldung.
- `qas` braucht **Write** für dieses Konto (veröffentlicht genügte nicht), dauert
  rund 50 s je Knoten und liefert `question`, `answer`, `usedText` — `created`
  im Jahr 58665.
- `respond` braucht eine Konfiguration für die Responses-API; die
  chat-Konfigurationen antworten 400, und der Anbieterfehler kommt als
  `{"error": {"message": …}}` — die Meldung liest ihn jetzt als Satz.
- Eine limited-Wahl füllt `var(X_DISPLAYNAME)` nicht; freier Text über limited
  erreichte den Prompt nicht. `topic_page_ai_default` merkt sich Antworten
  (`useCaching`).
- Importkosten am Ende: 1,36 ms (beide Template-Module), nichts sonst nachgeladen.
