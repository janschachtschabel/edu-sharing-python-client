# Design: der Volltextdienst

## Ziel

Den Textextraktionsdienst ansprechen, den eine edu-sharing-Instanz neben dem
Repositorium betreibt — damit auch der Text extern verlinkten Materials
erreichbar ist, den das Repositorium selbst nicht gespeichert hat.

## Kontext

Ich hatte `get_url_text` des MCP als „beliebige URL abrufen" eingeordnet und
mit SSRF-Begründung ausgeschlossen. Das war falsch gelesen. Das Werkzeug ruft
keinen fremden Server ab, sondern **den Extraktionsdienst der eigenen
Instanz** — bei WLO über `WLO_TEXT_EXTRACTION_URL`, auf Staging
`https://text-extraction.staging.openeduhub.net`.

Damit ist es dasselbe Muster wie die b-api: ein zweiter Dienst neben dem
Repositorium, eigenständig konfiguriert. Und es schließt eine Lücke, die ich
zu früh als geschlossen gezählt hatte: `content.text()` liest, was das
Repositorium gespeichert hat — für extern verlinktes Material ist das nichts.

## Am 28.08.2026 gemessen

Gegen `https://text-extraction.staging.openeduhub.net`, FastAPI, Version
`c766f2e5`:

1. **Drei Routen:** `/_ping`, `/from-url`, `/metrics`. Kein `/health`, kein `/`.
2. **`POST /from-url`**, Körper `{url*, method, browser_location, lang,
   output_format, preference}`. Nur `url` ist Pflicht. Vorgaben des Dienstes:
   `method="simple"`, `lang="auto"`, `output_format="txt"`,
   `preference="none"`. `method` ist ein Enum aus `simple` und `browser`.
3. **Antwort 200:** `{text, lang, status, version}`; Pflicht sind `text`,
   `lang`, `status`. `status` ist der HTTP-Status **der Zielseite**, nicht der
   des Dienstes.
4. **Antwort 424 statt 400.** Eine unbrauchbare URL, eine Seite ohne Text, ein
   privater Host — alles endet in `424 Failed Dependency` mit
   `{"detail": {"error_message", "status", "reason", "version"}}`. Ein
   fehlendes Pflichtfeld ergibt `422`.
5. **Eine edu-sharing-Download-URL ergibt 424.** Der Dienst kann nicht lesen,
   was das Repositorium selbst hostet — dafür bleibt `/textContent` zuständig.
   (Deckt sich mit der Messung des MCP vom 28.07.2026.)
6. **`ccm:wwwurl` ergibt 200** — im gemessenen Fall mit dem Hinweistext einer
   Seite, die JavaScript verlangt. Der Dienst liefert, was ohne Rendern da ist.
7. **`method="browser"` ist nicht einfach besser.** Auf `wirlernenonline.de`
   lieferte `simple` den Fließtext der Seite, `browser` den Text des
   Cookie-Banners. Beide Wege sind Versuche, keiner ist der bessere.
8. **Private Hosts beantwortet der Dienst mit 424**, nicht mit einem Fehler.
   Das ist kein Schutz, auf den sich diese Bibliothek verlassen darf: es ist
   *sein* Netz, nicht unseres, und das nächste Deployment kann anders liegen.

## Umfang

**Drin:**

- `src/edusharing/extraction.py` — `TextExtraction`, eigenständiger Client
  nach dem Muster von `BildungsAPI`: eigene Basis-URL, eigenes `from_env()`,
  eigener Kontextmanager. `ping()` und `text_of(url, …)`.
- `ExtractedText` als Ergebnisobjekt mit `reason`, wenn kein Text da ist.
- Schutz vor SSRF, bevor irgendetwas gesendet wird.
- Beide READMEs: der Dienst selbst und das Rezept „Volltext eines Knotens, aus
  welcher Quelle auch immer".

**Draußen:**

- **Kein Default für die Basis-URL.** Das MCP hat den Fehler gemacht und wieder
  zurückgenommen: ein Default auf den Staging-Dienst schickte
  Produktions-Material-URLs in eine andere Umgebung. Nicht gesetzt heißt: kein
  Client.
- **Keine Anbindung an `Repository`.** Die b-api hängt auch nicht daran. Ein
  zweiter Dienst wird eigenständig gebaut; wer beides braucht, hält beides.
- **Kein `flows.full_text`.** Aus demselben Grund: ein Ablauf hat nur `repo`.
  Die Verkettung steht als Rezept in den READMEs.
- **Keine Mindestlänge.** Das MCP wertet unter einer Schwelle als
  „gescheitert". Ob 40 Zeichen Text sind oder ein Rest, entscheidet der
  Aufrufer — `char_count` steht dafür in der Antwort.
- **Kein `/metrics`.** Prometheus-Format, keine Antwort auf eine Frage, die
  diese Bibliothek stellt.

## Sicherheit

Der Aufrufer wählt die URL, ein fremder Dienst ruft sie ab. Geprüft wird
**vorher**, in dieser Reihenfolge — billigste und sicherste Prüfung zuerst:

1. Schema ist `http`/`https`, sonst `reason="not_http"`.
2. Der Host ist keine private, Loopback-, Link-Local- oder reservierte
   IP-Literal-Adresse (`ipaddress` aus der Standardbibliothek), sonst
   `reason="private_host"`.
3. Der Host löst nicht in einen solchen Bereich auf
   (`loop.getaddrinfo`), sonst `reason="private_host"`; scheitert die
   Auflösung, `reason="dns_failed"` — verweigert statt durchgewunken, denn der
   Dienst löst womöglich auf, was wir nicht konnten.

Es bleibt eine Lücke, und sie lässt sich hier nicht schließen: zwischen unserer
Auflösung und der des Dienstes liegt ein Fenster, und eine Umleitung passiert
in seinem Prozess. Das steht im Modul, statt beschwiegen zu werden.

Geloggt wird nur der **Host**, nie die URL: eine vom Aufrufer gewählte URL kann
ein Token im Query tragen, und eine Verweigerung darf nicht das sein, was es
protokolliert.

## Schnittstelle

```python
@dataclass(frozen=True)
class ExtractedText:
    url: str            # normalisiert, wie gesendet
    text: str
    lang: str           # vom Dienst erkannt
    status: int         # HTTP-Status der ZIELSEITE
    char_count: int     # vor dem Kürzen
    truncated: bool
    reason: str         # "" wenn Text da ist

class TextExtraction:
    ENV_BASE_URL = "EDU_SHARING_TEXT_EXTRACTION_URL"

    def __init__(self, base_url: str, *, timeout=60.0, max_retries=2,
                 backoff_base=1.0, client=None) -> None: ...
    @classmethod
    def from_env(cls, **kwargs) -> TextExtraction: ...
    async def ping(self) -> dict[str, Any]: ...
    async def text_of(self, url: str, *, method: str = "simple",
                      output_format: str = "txt", lang: str = "auto",
                      max_chars: int | None = None) -> ExtractedText: ...
```

`reason` ist einer von `not_http`, `private_host`, `dns_failed`,
`no_text` — jeder mit eigener Ursache, damit „das würden wir nicht abrufen" nie
wie „die Seite hatte keinen Text" aussieht.

## Aufgaben

1. `tests/test_extraction.py` — Wertobjekt, Schutzprüfungen, 200, 424, 422,
   Kürzen. Rot vor dem Code.
2. `src/edusharing/extraction.py`.
3. Synchrone Hülle? **Nein** — `BildungsAPI` hat auch keine. Gleiche
   Begründung, gleiche Konsequenz.
4. Beide READMEs: Abschnitt zum Dienst, Rezept für den Volltext eines Knotens,
   Korrektur des Abschnitts „Was diese Bibliothek nicht tut".
5. Ein Live-Test gegen den Dienst, übersprungen ohne konfigurierte Basis-URL.

## Verifikation

| Kriterium | Befehl |
|---|---|
| Schutzprüfungen greifen vor jedem Senden | `pytest tests/test_extraction.py -k schutz` |
| 424 wird zu `reason`, nicht zu einer Ausnahme | `pytest tests/test_extraction.py` |
| Keine Rückschritte | `uv run pytest` |
| Live gegen den Dienst | `pytest -m live -k extraktion` |
