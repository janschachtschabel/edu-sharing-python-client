# Phase 5 — die Befunde, die in keiner Phase standen

Quelle: `docs/audits/2026-09-03-audit.md`, §6 „All findings". Die Roadmap in §9
ist abgearbeitet (Phasen 1–4). Nach dem letzten Commit von Phase 4 habe ich §9
gegen die Befundliste gemessen:

**Der Bericht führt 61 Befunde, §9 plant 44 davon ein.** Von den siebzehn
übrigen sind sechs Verweise (`DOC-8 = MNT-5`, `API-4 = SEC-8`, `DEP-3 = OPS-2`)
oder ausdrücklich positive Feststellungen (SEC-9, OPS-6, ARC-4 teilweise). Die
restlichen elf standen in keiner Phase — niemand hätte sie je angesehen.

Nachgemessen am 08.09.2026, mit Ausführung statt mit Mustersuche: **drei sind
zu** (PRF-1 über SEC-2, TST-2 über COR-1, TST-5), **neun sind offen**. Der
erste Anlauf mit Regexen meldete COR-8 fälschlich als behoben, weil das Muster
`dropping = {k.strip()…}` traf statt der Speicherung — dieselbe Lehre wie in
Phase 4: eine Prüfung, die aus dem falschen Grund grün ist, ist schlimmer als
keine.

Regeln wie bisher: Test zuerst, ein Commit je Befund, vor jedem Commit
`scratchpad/gate.sh` (ruff, mypy --strict, ganze Suite) mit direkt gelesenem
Exit-Code. Die drei mit *needs verification* werden nachgemessen, bevor etwas
geändert wird — in Phase 4 war jeder solche Befund beim Nachmessen anders als
beschrieben.

## Schritte

- [ ] **22 · COR-8** Leere und gepolsterte Schlagworte werden geschrieben.
  Im Bericht *verified*: `add_keywords("", "   ", " Optik ")` sendet
  `['Physik', '', ' Optik ']`. Verglichen wird gestrippt und kleingeschrieben,
  **gespeichert** aber der Rohwert — und ein leerer String besteht den
  Vergleich, solange noch kein leerer in der Liste steht.

- [ ] **23 · COR-6** `Vocabulary.clear_cache()` während eines laufenden
  Abrufs. Im Bericht *verified*: ein Abruf startet, `clear_cache()` dazwischen,
  der fertige Abruf schreibt die alten Werte in den geleerten Speicher zurück.
  Wer leert, weil sich das Vokabular geändert hat, bekommt den alten Stand
  zurück, ohne es zu merken.

- [ ] **24 · COR-10** Ein `CancelledError` eines Kindes wird als
  fehlgeschlagener Zweig gezählt. Zwei Stellen, `collections.py` und
  `flows/rerank.py`. **Dieselbe Klasse wie die Regression, die Schritt 14
  fand**: `gather(return_exceptions=True)` gibt jede Ausnahme als Wert zurück,
  und wer nicht nach dem Typ fragt, macht aus einem Abbruch oder einem 500 eine
  Teilantwort. `search_all` und `placement` reichen es bereits weiter.

- [ ] **25 · COR-11 und COR-7** Die zwei Rückvergleiche, beide *needs
  verification*. `update(description="")` könnte einen falschen
  `SilentDropError` werfen, weil `Node.get` für eine leere Eigenschaft `None`
  liefert; und `check()` verlangt exakte Listengleichheit, was bei einem Server,
  der umsortiert oder trimmt, dasselbe auslöst. Erst messen.

- [ ] **26 · COR-9** Falsy Skalare gelten als abwesend. `Node.get` und
  `results._first` geben `None` für eine `0` oder ein `False` zurück,
  `flows/serialize.py` behält sie. Eine Regel für beide.

- [ ] **27 · API-3** `collection_contents` deckelt die Untersammlungen bei
  `limit`, ohne `total` und ohne Kennzeichen — dieselbe Bauform wie MNT-4, das
  Phase 4 gerade behoben hat.

- [ ] **28 · ARC-3** Die Importzyklen. Der Bericht sagt selbst „not a bug today
  (fresh-interpreter import of every module verified)" und schlägt eine
  `Nodes.wrap`-Fabrik vor. Zuletzt, weil es das einzige ist, das nichts
  repariert.
