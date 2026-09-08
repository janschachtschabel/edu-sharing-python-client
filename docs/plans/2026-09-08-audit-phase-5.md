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

- [x] **22 · COR-8** Leere und gepolsterte Schlagworte, `59b6568`.
  Verglichen wurde gestrippt und kleingeschrieben, **gespeichert** der
  Rohwert — und ein leerer String bestand den Vergleich, solange noch kein
  leerer darin stand. `cclom:general_keyword` ist eine geteilte Liste: ein
  leeres Schlagwort ist in jeder Anzeige eine leere Zeile und in jeder Facette
  ein Eintrag ohne Namen, und weil die Liste geteilt ist, sieht ihn jeder, der
  danach hineinschaut.

- [x] **23 · COR-6** `clear_cache()` während eines laufenden Abrufs, `4f94929`.
  Eine Generationszählung, vor dem `await` gelesen. Der laufende Abruf liefert
  weiterhin an seinen Aufrufer; er füllt nur den Cache nicht mehr, denn seine
  Werte sind von vor dem Leeren. Nachgestellt mit einer Antwort, die auf ein
  Ereignis wartet — so liegt das Leeren nachweislich *im* Abruf.

- [x] **24 · COR-10** Ein Abbruch ist kein Teilausfall, `179243a`.
  Zwei Stellen fragten nicht nach dem Typ. Beim Nachmessen zwei **weitere**
  `gather`-Stellen geprüft und bewusst nicht geändert: `fields.py` wärmt nur
  vor und verwirft begründet, `skills.py` trägt seit Schritt 14 die engere
  Regel. Mein erstes Suchmuster hatte beide fälschlich gemeldet.

- [x] **25 · COR-11 und COR-7** Die zwei Rückvergleiche, `7f279e5`.

  **COR-11 trifft zu, aber nur zur Hälfte.** Der Fehler tritt nur auf, wenn
  der Server die geleerte Eigenschaft **weglässt**; gibt er sie als leere
  Liste zurück, stimmte der Vergleich schon. Beide Formen sind jetzt gebunden.

  **COR-7 trifft nicht zu — live gemessen.** Die Sorge war, `check()` sei mit
  seinem exakten Listenvergleich zu streng für ein Repositorium, das
  umsortiert oder trimmt. Gegen edu-sharing 11.0 (Staging), im eigenen
  Wegwerf-Ordner: es tut beides nicht. `["Zebra", "Mitte", "Anfang"]` kommt in
  dieser Reihenfolge zurück — absichtlich absteigend geschrieben, weil eine
  aufsteigende Liste auch eine Sortierung unverändert überstünde — und
  `" Rand "` behält seine Leerzeichen. Die Strenge bleibt, und zwar gemessen
  statt geraten: ein Vergleich, der eine Umsortierung durchgehen lässt, lässt
  auch einen Verlust durchgehen. Zwei Live-Tests halten die Messung fest.
  Nicht gemessen: die Normalisierung von Datumsangaben — hier schreibt nichts
  ein Datumsfeld.

- [x] **26 · COR-9** Eine Null ist ein Wert, `fe51c56`.
  **Hier wurde ein bewusst getesteter Vertrag geändert**, nicht ein Versehen
  behoben: der alte Fall stand mit `(0, None)` im Test und mit einer
  Begründung im Docstring. Die Begründung war falsch. Jeder Aufruf von `first`
  liest `properties.get(...)`, der Skalarzweig ist also ein Sicherheitsnetz —
  und eines, das `0` verschluckt, macht bei `cclom:size` aus „0 Bytes" ein
  „keine Größe". Die zweite Hälfte des Befunds ist veraltet: ein eigenes
  `_first` in `results.py` gibt es seit MNT-1 nicht mehr.

- [x] **27 · API-3** Die Untersammlungen nennen ihre Anzahl, `6e6513d`.
  Vorher gemessen, ob der Endpunkt überhaupt eine Gesamtzahl nennt — das ist
  nicht selbstverständlich, `ngsearch` antwortet mit `pagination: null`. Gegen
  Staging: bei `maxItems=1` an einer Sammlung mit zwei Untersammlungen kommt
  **ein** Eintrag und `total: 2`.

- [x] **28 · ARC-3** `Nodes.wrap` löst vier Rumpfimporte ab, `ee31dc1`.
  Der fünfte bleibt, mit Begründung im Wächter: `skills` und
  `skills_registry` sind zwei Hälften einer Sache, und ein Import im Rumpf
  sagt das ehrlicher als der Re-Export, den der Bericht vorschlägt.

Damit ist der Bericht vollständig abgearbeitet — die 44 Befunde der Roadmap
und die elf, die in keiner Phase standen.
