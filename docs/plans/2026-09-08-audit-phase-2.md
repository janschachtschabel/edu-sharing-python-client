# Phase 2 der Audit-Roadmap — Fundamente

Quelle: `docs/audits/2026-09-03-audit.md` §9, Schritte 6–11. Phase 1 ist
abgeschlossen (`docs/plans/2026-09-03-audit-phase-1.md`).

Regeln wie in Phase 1: Test zuerst, ein Commit je Befund, vor jedem Commit
`scratchpad/gate.sh` (ruff, mypy --strict, ganze Suite) mit direkt gelesenem
Exit-Code. Live nur auf der Staging, nur in selbst angelegten Wegwerf-Ordnern.

## Schritte

- [x] **6 · ARC-2 + API-2** Eine Wiederholungs-Regel für drei Schleifen:
  `retry.py` mit dem wiederholbaren Statussatz, Budget, Backoff **mit Jitter**
  und `Retry-After`. `RateLimitedError` für den 429, in allen drei Schleifen
  beachtet. Der Transport behält seine Einordnung nach Fehlertyp.
  Getan: `retry.py` mit `RetryPolicy`, `RETRYABLE_STATUS`, `parse_retry_after`;
  der 429 wird auch bei einem Schreibvorgang wiederholt, weil er eine Absage
  und kein Ergebnis ist; eine zu lang genannte Wartezeit kommt mit der Zahl
  beim Aufrufer an. Der Feldwächter der Doku kennt jetzt auch geerbte
  Konstruktorfelder, und die Extraktion prüft erstmals ihr `backoff_base`.
- [x] **7 · MNT-1** `dto.py`: ein Knotensatz, einmal gelesen — für `Node`,
  `SearchHit`, Skills und Seiten. Heute steht derselbe Titel je nach Objekt
  anders da.
  Getan in zwei Commits: erst `dto.py` mit `first`, `node_id_of`, `bare_id`,
  `render_url`, `page_total` und zwoelf umgestellten Modulen, dann `title_of`
  als die eine Titelkette. Nicht zusammengefuehrt: die drei `as_list`-artigen
  Funktionen -- sie tun Verschiedenes (schreiben, lesen, aus einem Iterable
  eine Liste machen) und sind keine Kopien.
- [x] **8 · ARC-1** `fields`, `ranking`, `language` aus `flows/` heraus,
  `cap_text` aus `agent/` heraus; dazu ein Test über die Import-Richtung.
  Getan: die drei Module per `git mv` eine Schicht tiefer, `cap_text` in das
  neue `strings.py`, `field_property` zu `fields.py` (es löst einen Namen auf,
  es sucht nicht). `tests/test_import_direction.py` liest die Kanten per AST;
  Ausnahmen sind nur `repository.py` und `__init__.py`, benannt und begründet.
- [x] **9 · COR-5 + COR-3** Die Schreibabläufe behalten die angelegte id, wenn
  ein späterer Schritt scheitert; Rücklesen prüft gegen einen Stand von **vor**
  dem Schreiben, nicht gegen Textgleichheit.
  Getan in zwei Commits: COR-5 (`_place`/`_publish` melden in `warnings`,
  `build_collection` bekam den Schlüssel) und COR-3 (`comments.add` merkt
  sich die ids, `workflow.submit` die Länge des Verlaufs -- je eine Anfrage
  mehr, dafür ein `SilentDropError`, auf den Verlass ist).
- [x] **10 · TST-1 / MNT-2 + COR-4** Der Spiegel wird auf Verhalten geprüft und
  bekommt echte Rückgabetypen; der Schleifen-Thread wird auch bei gescheiterter
  Konstruktion geschlossen.
  Getan in zwei Commits: COR-4 (asynchrone Seite zuerst, `weakref.finalize`,
  `close()` wirft nicht mehr über eine Schleife, die stehen bleibt) und TST-1
  (der Wächter ruft vierzehn Spiegelpaare wirklich auf, samt Gegenbeweis).
  Offen aus MNT-2: die 67 `Any`-Annotationen der Spiegel -- die Wache deckt
  jetzt das Verhalten ab, die Typen bleiben für Phase 3.
- [x] **11 · DEP-2 / DEP-1 / OPS-1** Regenerierung gepinnt und mit Herkunft
  vermerkt, Phantom-Abhängigkeiten weg, CI mit `--locked`.
  Getan. Der Fund unterwegs: der Generator muss im Projekt laufen, dann wählt
  er `typing.Self` und die Zeilenbreite selbst -- außerhalb ergeben dieselbe
  Spec und derselbe Generator 556 anders geformte Dateien. Nach der
  Regenerierung bleiben vier Dateien mit bedeutungsgleicher Union-Reihenfolge;
  ein zweiter Lauf ändert nichts mehr.

Damit ist Phase 2 abgeschlossen. Weiter mit Phase 3 der Roadmap (§9).

## Review-Nachlese (08.09.2026)

Ein frischer Durchgang über den ganzen Phase-2-Diff: 3 MAJOR, 7 MINOR,
5 NIT. Jeder Befund am Quelltext geprüft und reproduziert, bevor etwas
geändert wurde.

- [x] **F1 MAJOR** `Retry-After` galt für **jede** Fehlerantwort, nicht nur
  für den 429. Damit bestimmte ein Proxy-Kopf den Backoff jedes 5xx (drei
  Pausen von je 30 s statt 0,5–2 s) und ein langer Wert nahm alle
  Wiederholungen; der Fehler kam obendrein als `ServerError` an, sodass die
  dokumentierte Prüfung auf `RateLimitedError` ihn nie sah → nur noch der 429
  trägt die Zahl, an allen drei Bau-Stellen (`d3b9ecf`).
- [x] **F2 MAJOR** Der Verlaufsbeweis zählte nur die Länge und suchte dann im
  **ganzen** Verlauf: wächst er aus fremdem Grund, wurde der alte gleiche
  Schritt als der neue gemeldet → gesucht wird nur im neuen Präfix
  (`bb2dff7`).
- [x] **F3 MAJOR** Die vereinheitlichte Titelkette fällt auf `cm:name` zurück;
  `collections.update` schrieb den so gelesenen Namen bei einer Sammlung ohne
  Titel nach `cm:title` → neues `dto.stored_title_of` für die Schreibseite.
  Dazu die Doku, die der Kette hinterherhing (`476e7dd`).
- [x] **F4 MINOR** Der Richtungswächter übersah `from . import x` (die Form,
  die `nodes.py` benutzt) und befreite über den Dateinamen auch
  `flows/__init__.py` (`4de5fe0`).
- [x] **F5/F6/F11 MINOR/NIT** `build_collection`s `warnings` und `public` in
  beiden Referenzen, der Docstring von `add_material`, „fünf Funktionen" →
  sieben (`476e7dd`).
- [x] **F7 MINOR** `--from-instance` nannte den Hash einer Bytefolge, die es
  nirgends gab → die geholte Spec wird geschrieben, dann gehasht (`4de5fe0`).
- [x] **F8 MINOR** `page_total` gab bei einem ausdrücklichen `total: 0` die
  Vorgabe zurück (`4de5fe0`).
- [x] **F9 MINOR** Das Vorher-Lesen ist eine neue Voraussetzung fürs
  Schreiben; beide Docstrings sagen sie jetzt (`4de5fe0`).
- [x] **F10 MINOR** Die Abhängigkeitswache hätte bei leerer Liste geschwiegen
  statt zu scheitern (`4de5fe0`).
- [x] **F12/F13/F15 NIT** `first([None])`, `DEFAULT_MAX_RETRY_AFTER`
  exportiert und dokumentiert, vier deutsche Kommentare im englischen
  Quelltext übersetzt (`4de5fe0`).
- [-] **F9, zweiter Teil** `comments.add` zusätzlich am Autor erkennen: nicht
  gemacht. Der Vergleich der ids schließt jeden Kommentar aus, der vorher
  schon dastand; offen bleibt nur, dass jemand anderes in derselben
  Millisekunde denselben Text schreibt. Den eigenen Autorennamen zu kennen
  kostete ein zusätzliches `whoami` bei jedem Kommentar — das wiegt schwerer
  als der Rest dieses Rennens.
- [x] **F14 NIT** Der Zweig, der eine zu lange Wartezeit weiterreicht, kann
  seit F1 nur noch einen 429 sehen; der Kommentar sagt das, statt `_noted`
  als Blindleistung zu rufen.

Als sauber gemeldet und nachgeprüft: `weakref.finalize` hält den
`LoopThread`, nicht das Repositorium, und `close()` bleibt einmalig; der
Spiegelwächter ist nicht leerlaufend; `parse_retry_after` liest beide
Schreibweisen richtig; keine Doku steht nur in einer Sprache.
