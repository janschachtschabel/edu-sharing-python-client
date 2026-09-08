# Phase 4 der Audit-Roadmap — Politur

Quelle: `docs/audits/2026-09-03-audit.md` §9, Punkt 16. Phase 3 ist
abgeschlossen (`docs/plans/2026-09-08-audit-phase-3.md`), samt Review-Nachlese.

Regeln wie bisher: Test zuerst, ein Commit je Befund, vor jedem Commit
`scratchpad/gate.sh` (ruff, mypy --strict, ganze Suite) mit direkt gelesenem
Exit-Code. Live nur auf der Staging, nur in selbst angelegten Wegwerf-Ordnern.

Punkt 16 bündelt acht Befunde in einer Zeile. Zwei davon waren beim
Nachmessen schon zu: **OPS-4** (`.gitattributes`) wurde in Schritt 14
vorgezogen, weil es die Ursache des ersten roten Windows-Laufs war. Und
**MNT-3s zweite Hälfte** — „`request`, C=10, drei ineinandergreifende
Wiederholungsbudgets" — hat ARC-2 in Phase 2 erledigt: gemessen am 08.09.2026
hat `Transport.request` **eine** Schleife und C=8. Geprüft, nicht „behoben"
gemeldet.

## Schritte

- [x] **16 · SEC-5, SEC-6, SEC-7** Die drei Befunde an der Modellgrenze.
  Getan in drei Commits: `2c7c59c` (Fremdtext auf dem Fehlerweg bleibt eine
  Zeile), `436b90b` (eine Umleitung nennt ihr Ziel, nicht die ganze Adresse),
  `cce9e42` (ein mimetype muss ein Typ sein, keine Kopfzeile).

  **SEC-5 hatte zwei Hälften, und die zweite stand direkt neben der Lösung.**
  `format_results` flacht Warnungen und Korrekturvorschläge mit `one_line` ab
  — den unaufgelösten Filter eine Zeile darüber nicht, obwohl dessen `__str__`
  gleich drei Server-Angaben zusammensetzt. Dieselbe Lücke wie beim Titel in
  Audit A1, nur über den Fehlerweg.

  **SEC-6 zeigte, wie eine gute Fehlermeldung schlecht wird.** Der Text nannte
  die volle `Location`, damit die Meldung nützlich ist — und reichte damit
  vorsignierte Adressen und Anmelde-Tickets in die Logs und in den
  Modellkontext weiter. Der Host beantwortet dieselbe Frage („mein Proxy oder
  ein Fremder?") ohne das Geheimnis; der volle Wert steht als `exc.location`,
  nach dem Muster von `retry_after`. Beim Schreiben fiel auf, dass der
  Nachsatz „die ganze Adresse steht als `.location`" bei einem 304 ohne
  `Location` auf ein leeres Attribut zeigte — eine Meldung, die jemanden auf
  die Suche schickt, ist genau das, was dieses Projekt sonst bekämpft.

  **SEC-7 war als *verified* geführt und ist nachgemessen.** httpx 0.28.1
  schreibt `Content-Type: <mimetype>` ungeprüft; ein `\r\n` erzeugt eine
  zweite Kopfzeile. Beim Nachmessen kam eine Frage dazu, die der Befund nicht
  stellt: **auch der Dateiname geht in dieselbe Kopfzeile.** Den kodiert httpx
  (`%0D%0A`) — die Lücke ist also genau auf den Inhaltstyp begrenzt, und das
  ist eine Antwort und keine Vermutung.

- [x] **17 · OPS-5** Der Umfang des Quellpakets, `1a6840f`.

  Im Bericht als *needs verification* geführt: kein Build war gelaufen. Jetzt
  gebaut. Ohne eigenen Abschnitt nahm hatchling alles, was git kennt — 1318
  Dateien, 1,2 MB, darunter `.claude/`, `.github/`, `uv.lock` und die 1,3 MB
  große Spezifikation. Jetzt 1204 Dateien und 556 KB.

  **Die dringlichste Frage stellte der Befund nicht:** ob `.env` mitgeht. Es
  liegt im Wurzelverzeichnis und trägt die Zugangsdaten. Gemessen: nein —
  hatchling liest `.gitignore`. Das hing aber an einer Voreinstellung, die
  niemand aufgeschrieben hatte; mit einer Positivliste hängt es an nichts
  mehr.

  **Eine Positivliste, keine Ausschlussliste.** Eine Ausschlussliste veraltet
  mit jedem neuen Ordner — was dazukommt, wird ausgeliefert, bis jemand daran
  denkt. Dieselbe Lehre wie aus DOC-5, nur in die andere Richtung: eine
  Einschlussliste *kann* nicht unvollständig werden, sie ist die Definition.

  **Die Suite bleibt draußen, und das ist die eigentliche Entscheidung.** Sie
  prüft das *Repositorium*: `test_docs_*` liest `docs/`, `test_dependencies`
  liest `uv.lock` und die Spezifikation, `test_no_secrets` durchsucht
  `.github/` und `.claude/`. Fehlen die, läuft keine dieser Wachen rot —
  `rglob` über einen Ordner, den es nicht gibt, liefert nichts. Eine Suite,
  die im Quellpaket aus dem falschen Grund grün ist, verspricht eine
  Prüfbarkeit, die es dort nicht gibt. Nachgemessen: aus dem entpackten Paket
  importieren 1193 Module ohne Fehler, `py.typed` ist dabei.

- [x] **18 · MNT-4** Der stille Deckel, `4fda0d4`.

  `list()` nahm hart `maxItems=200` und sagte nichts, wenn es mehr gab — die
  einzige Auflistung dieser Bibliothek, die kürzt, ohne es auszuweisen. Jetzt
  heißt der Deckel `LIST_MAX` und was darüber liegt, wirft: es gibt keine
  Verwendung, für die die ersten 200 richtig wären, und `list[Node]` hat
  keinen Platz für „unvollständig". Sagt der Server keine Gesamtzahl, wird
  nicht geworfen — die Wache gilt dem, was er nennt.

  `add()` brauchte nur eine Zahl und holte dafür bis zu 200 Datensätze mit
  `propertyFilter=-all-`. Eine Seite mit einem Eintrag trägt dieselbe
  Gesamtzahl. **Die Zahl der Anfragen bleibt** — der Befund nennt „3N
  Anfragen", und daran ändert der vorgeschlagene Fix nichts; ihre Größe sinkt.

  Die neue Zählung sieht jedes Kind, auch Versionen, während `list()` danach
  auf den Aspekt filtert. Die Position überspringt also Nummern. Zugesagt ist
  *hinter den bestehenden*, nicht *lückenlos* — eine Nummer zu überspringen
  kostet nichts, zwei Anhänge auf einer Position kosten die Reihenfolge.

- [x] **19 · MNT-5** Die zwanzig Member ohne Docstring, `1a0d963`.

  Nachgemessen: dieselben zwanzig wie am 03.09.2026. Ein erster Messversuch
  fand 26 — und lag falsch: sechs davon sind Datenfelder, von denen zwei
  (`VocabularyValue.uri/label`) `#:`-Kommentare tragen, die ein
  `__doc__`-Vergleich nicht sieht.

  Das entschied den Zuschnitt der Wache. `tests/test_docstrings.py` verlangt
  Docstrings für Klassen, Methoden und Eigenschaften — **nicht** für
  Datenfelder. Ein `#: The value.` über `value: str` wäre Nacherzählung; wo
  ein Feld mehr trägt als seinen Namen, steht es als `#:`-Kommentar dabei. Was
  ein Urteil braucht, bewacht sie nicht.

- [x] **20 · MNT-3** Die dreizehn Parameter, `b606c53` und `d113f1e`.

  **`SearchOptions` habe ich abgelehnt.** Der Bericht schlägt eine Dataclass
  für die dreizehn Knöpfe von `search` vor. Die Faustregel „mehr als fünf
  Parameter → ein Objekt" zielt auf *positionale* Parameter, wo die
  Reihenfolge zur Falle wird; hinter einem `*` gibt es diese Falle nicht.
  `repo.flows.search("Bruchrechnung", subject="Mathematik", limit=10)` ist die
  natürliche Form der meistbenutzten Methode dieser Bibliothek, und
  `search(SearchOptions(...))` wäre für jeden Aufrufer schlechter. Ein
  Umstellen bräche außerdem jedes Beispiel und jeden bestehenden Aufruf, für
  eine Regel, die hier nicht greift.

  Was der Befund **richtig** sieht, ist die Wiederholung: die Signatur steht
  viermal da — in `find.search`, in der Signatur von `Flows.search`, im
  Weiterleitungsaufruf darunter und in `_sync.SyncFlows`. Für die letzte
  Stelle gibt es die Wache seit Review C6; für die Ebene davor gab es keine.
  Wer `find.search` einen Knopf hinzufügt und `Flows.search` vergisst, bricht
  nichts — der Knopf ist über `repo.flows.search` nur nicht da, und
  `**aliases` schluckt ihn als Metadatenfeld, sodass es nicht einmal einen
  `TypeError` gibt.

  `tests/test_flows_surface.py` bindet beide Richtungen und die Vorgaben für
  alle 26 Methoden. **Beim Bauen wäre mir fast derselbe Fehler passiert wie in
  Phase 3:** die erste Fassung leitete den Ausweg ab („hat `**kwargs`, also
  erlaubt") — und hätte damit ausgerechnet `search` freigestellt, den einen
  Fall, um den es geht. Jetzt steht eine benannte Liste da, und zwei weitere
  Wachen halten sie knapp und frei von Karteileichen.

  Die Wiederholung selbst bleibt, mit Absicht: sie kauft die Typisierung und
  die Vervollständigung im Editor, die ein `**kwargs`-Durchgriff verlöre — bei
  einer Bibliothek mit `py.typed` und `mypy --strict` ist das der teurere
  Verlust.

  Dazu `load_registry`: mit C=10 die einzige Funktion genau an der erlaubten
  Grenze, auf 110 Zeilen mit drei Themen. Zwei davon haben klare Nähte und
  sind heraus; C=6 und 82 Zeilen. Vorher die Abdeckung geschlossen — die zwei
  Zeilen, die kein Test erreichte, tragen ausgerechnet die Unterscheidung, um
  die es geht: eine Aussage über die Sammlung wird zum Grund, alles andere
  fliegt weiter.

Danach: die Roadmap ist abgearbeitet.
