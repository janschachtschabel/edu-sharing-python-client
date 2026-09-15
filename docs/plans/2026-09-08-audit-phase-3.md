# Phase 3 der Audit-Roadmap — Verbesserung

Quelle: `docs/audits/2026-09-03-audit.md` §9, Schritte 12–15. Phase 2 ist
abgeschlossen (`docs/plans/2026-09-08-audit-phase-2.md`), samt Review-Nachlese.

Regeln wie bisher: Test zuerst, ein Commit je Befund, vor jedem Commit
`scratchpad/gate.sh` (ruff, mypy --strict, ganze Suite) mit direkt gelesenem
Exit-Code. Live nur auf der Staging, nur in selbst angelegten Wegwerf-Ordnern.

Diese Phase betrifft zum ersten Mal alle **vier** Clients gleichermaßen: den
Transport und seine drei Nachbardienste (Extraktion, Metadata-Agent, b-api).
Was der Transport gelernt hat, fehlt den dreien — das ist der rote Faden von
Schritt 12.

## Schritte

- [x] **12 · SEC-4, SEC-8, API-1, SEC-3** Die Wachen, die nur in einem Client
  stehen, in gemeinsamen Code.
  - SEC-4: ein eingeschleuster Client mit `follow_redirects=True` hebelt die
    3xx-Wache aus. httpx behält eigene Kopfzeilen über Ursprungsgrenzen hinweg,
    also wandert der `X-API-KEY` dorthin, wohin ein Gateway zeigt (gemessen).
    Alle vier Konstruktoren müssen das ablehnen, mit derselben Formulierung wie
    beim `timeout`.
  - SEC-8: `timeout` wird in der Extraktion geprüft und dann mit einem Client
    verworfen; `backoff_base` wird nie geprüft (`-1`, `nan` gehen durch).
  - API-1: `json.JSONDecodeError` entkommt dem `EduSharingError`-Vertrag. Eine
    200-Antwort mit HTML-Körper (Proxy-Loginseite) wirft eine Ausnahme aus der
    Standardbibliothek, die `agent.result.as_result` nicht fängt. Dazu die
    3xx-Behandlung, die nur der Transport hat.
  - SEC-3: `extraction.text_of` leitet Adressen weiter, die `agent.safety`
    ablehnt — `http://127.0.0.1\@example.com/` und Anmeldedaten im Netloc.

  Getan in vier Commits: `ec51ab7` (eine `check_client`-Wache, vier
  Aufrufer), `a6f7994` (`redirect_error` und `non_json_error` für alle
  vier), `d5df08a` (die Adressregel verhaltenserhaltend nach `urls.py`)
  und `1aec372` (`unsafe_url_syntax`, von Agent und Extraktion gerufen).
  Der Befund SEC-3 war als *needs verification* geführt und ist
  nachgemessen: `urlsplit` liest `http://127.0.0.1\@example.com/` als
  `example.com`, ein WHATWG-Parser als `127.0.0.1`.
  Beim Zuschnitt einmal zu grob gegriffen — der erste Anlauf rief
  `unsafe_url_reason` ganz und hätte `private_host` und `dns_failed` durch
  `unsafe_url` ersetzt; dreizehn Tests haben das gezeigt, geteilt wird
  seitdem nur die Schreibweisen-Hälfte.
- [x] **13 · PRF-2, PRF-3, PRF-4, PRF-5** Die Deckel und die Bündel.
  - PRF-2: `describe_many` ist das einzige unbegrenzte Fan-out.
  - PRF-3: serielle `await`s, wo die Aufrufe unabhängig sind. Enthält zwei
    Punkte, die der Bericht selbst als *needs verification* führt.
  - PRF-4: der Vokabular-Cache läuft nie ab, obwohl ARCHITECTURE eine TTL
    behauptet.
  - PRF-5: `add_material` fragt bei jedem Aufruf ohne `parent_id` erneut
    `whoami()`.

  Getan in vier Commits: `a7bbcb8` (Deckel für `describe_many`),
  `df865c0` (Ebene als Bündel im Skills-Gang, vorgewärmte Vokabulare,
  zwei richtiggestellte Begründungen), `f35eb9e` (TTL und
  Vorschlagsdeckel) und `b0c4179` (`whoami` je Zugangsdaten).

  Die zwei *needs-verification*-Punkte sind nachgemessen:
  `REGISTRY_POOL` (10) bindet über dem Vorrat des Transports (8) bei
  Vorgabe tatsächlich nie — tot ist die Schranke deswegen nicht, sie ist
  die eigene Obergrenze des Flusses und gilt, sobald jemand den Transport
  weiter öffnet; der Docstring sagt jetzt beides. Und das „Rennen" um die
  Dublettenmenge in `flows/tree.py` gibt es nicht: zwischen der Prüfung
  und dem `seen.add` steht kein `await`. Der wirkliche Grund, seriell zu
  bleiben, ist die Antwort — welcher Zweig eine von zwei Eltern
  erreichbare Sammlung bekommt, und was der Deckel abschneidet, hinge
  sonst davon ab, welche Anfrage zuerst zurückkommt.

  **Offen und bewusst nicht getan:** `build_collection` legt seine
  Referenzen weiterhin nacheinander ein. Das sind Schreibvorgänge gegen
  dieselbe Sammlung; ob die Instanz sie nebeneinander gleich behandelt,
  ist nicht gemessen. Ein Fan-out von Schreibvorgängen ohne Messung wäre
  geraten. Wer das aufgreift: erst live auf der Staging messen, dann
  entscheiden.
- [x] **14 · TST-3, TST-6, OPS-2, OPS-3** Aufräumen, Pins, CI und die
  geschriebenen Abläufe.
  Getan in fünf Commits: `9396854` (Wegwerf-Objekte werden weggeworfen),
  `6b9c3bb` (die drei Pins — und der erste fand sofort eine Regression aus
  meinem eigenen `df865c0`: `gather(return_exceptions=True)` fing **jede**
  Ausnahme und zählte einen 500 als „unlesbar"), `4b42925` (CI gehärtet,
  Windows-Lauf, `SECURITY.md`, Veröffentlichungs-Ablauf), `7042322` (ein
  roter Lauf sagt jetzt, woran er scheitert) und `684f633`
  (`.gitattributes`).

  **Der Windows-Lauf hat beim ersten Mal sofort etwas gefunden** — genau
  wofür der Befund ihn verlangt hat. Der Herkunfts-Hash aus DEP-2 stimmte
  dort nicht, weil ein Checkout auf Windows LF zu CRLF macht und der Hash
  Bytes zählt. Das ist OPS-4, eigentlich Phase 4, hier vorgezogen: es war
  die Ursache, nicht ein Symptom. Der Index war schon durchgehend LF, also
  kostet die Regel keinen einzigen Inhaltsunterschied.

  Der Log eines Laufs ist nur angemeldet lesbar. Ich habe mich **nicht**
  angemeldet, sondern die Ausgabe über eine Annotation öffentlich gemacht —
  das ist ohnehin die bessere Lösung, und die Diagnose lief danach in einem
  Durchgang.

  **Nicht gemacht:** der Abhängigkeits-Cache, den OPS-2 auch nennt. Dafür
  bräuchte es eine weitere fremde Action im Vertrauenskreis, und sie spart
  gegen einen Lauf von gut einer Minute wenige Sekunden. Der Tausch lohnt
  nicht.

  **Zu TST-6, dritter Pin:** der `unresolved`-Zweig in `find_by_url` ist
  über diesen Weg **nicht erreichbar** — das Schema wird davor geprüft und
  `resolve_all` reicht jede URI durch. Ein Test, der ihn künstlich
  erzwingt, hielte Fiktion fest; stattdessen pinnt der Test die Annahme,
  auf der die Unerreichbarkeit beruht.
- [x] **15 · DOC-3 bis DOC-7** Der Architektur-Nachweis, die Zahlen, die
  Beispiele und die Docstrings — die Zahlen möglichst abgeleitet, damit die
  Wächter sie besitzen statt der Prosa.
  Getan in acht Commits: `80b89c6` (DOC-6, die Beispiele lesen die Variable,
  die es gibt), `1c6d97e` (DOC-5, die Verzeichnisse zählen auf, was es gibt),
  `b193019` (DOC-4, keiner der drei Dienste trägt eine Vorgabeadresse),
  `a3fd5f2` (DOC-3, zehn fehlende Module und fünf falsche Zahlen), `58562b0`
  (DOC-7, die Warnstellen), dann nach der Prüfung `8702a8c` (die Wachen halten,
  was sie versprechen), `01e7328` (sieben Aussagen, die keine Wache sieht) und
  `9f3a06f` (eine doppelte Zuweisung).

  **Der Wächter für DOC-6 war um die Abweichung herum gebaut.** Es gab ihn
  schon — „jeder in der Dokumentation genannte Variablenname kommt im Code
  vor" — und er nahm als Beleg ausdrücklich auch ein Vorkommen im
  Beispielordner, mit `EDU_SHARING_MDS` als genanntem Beispiel im Docstring.
  Die Abweichung war der Wache beigebracht worden, nicht behoben. Jetzt zählt
  nur `src/`, und der alte Test ist strenger als vorher.

  **DOC-7 war schlimmer als gemeldet.** Der Befund zählte fünf WARNING-Stellen
  statt der behaupteten vier; es sind sieben. Dazugekommen waren die
  abgewiesene Adressschreibweise aus SEC-3 und die Hintergrundschleife, die
  nicht anhält, aus COR-4 — ausgerechnet in dem Abschnitt, der erklärt, warum
  diese Bibliothek sonst schweigt. Zwei andere Teile von DOC-7 waren beim
  Nachmessen bereits behoben; sie sind geprüft, nicht „behoben" gemeldet.

  **Die Prüfung fand drei MAJOR, und alle drei waren echt.** Der wichtigste
  traf meine eigene Wache: sie nahm als Beleg auch den blossen Dateinamen, und
  `collections.py` steckt als Teilzeichenkette in der Zeile für das *andere*
  Modul dieses Namens — `flows/collections.py` stand damit in keiner Tabelle,
  und die Wache schwieg. Eine Wache, die aus dem falschen Grund grün ist, ist
  schlimmer als keine. Das Verschärfen legte die eigentliche Lücke frei: §8.6
  führte alle Ablaufmodule in **einer** Sammelzeile, die sieben von fünfzehn
  nannte und vollständig aussah — genau die Bauform, gegen die DOC-3 sich
  richtet. Die anderen beiden: die deutsche README trug „über alle 20 Abläufe"
  weiter, und vier Stellen sagten, Vorschläge hätten keinen Ablauf, während
  `accept_suggestion` neun Zeilen weiter oben als Ablauf steht.

  Alle fünf Wachen sind mutationsgeprüft — Doku kaputtmachen, Test muss rot
  werden. Vier Mutationen einzeln nachgewiesen.

  **Nicht gemacht:** ein Wächter über die drei Kantenzahlen in §8.8 („sieben
  der fünfzehn", „auf fünf", „vier von ihnen"), den die Prüfung anregt. Die
  *Listen* sind Zusagen — unvollständig führen sie in die Irre. Die
  Kantenzahlen sind eine datierte Messung, die eine Aussage belegt („innerhalb
  dieses Pakets gibt es keine Richtungsregel"), und sie stehen unter demselben
  „Gemessen am …" wie die Zeilenzahlen von `nodes.py`, für die dieselbe
  Entscheidung schon getroffen wurde. Ein Wächter darüber schlüge bei jedem
  ordentlichen Umbau an, ohne dass etwas falsch wäre.

Danach: Phase 4 (Politur) der Roadmap.
