# Phase 5 — die Befunde, die in keiner Phase standen

Quelle: `docs/audits/2026-09-03-audit.md`, §6 „All findings". Die Roadmap in §9
ist abgearbeitet (Phasen 1–4). Nach dem letzten Commit von Phase 4 habe ich §9
gegen die Befundliste gemessen:

**Der Bericht führt 61 Befunde, §9 plant 44 davon ein.** Von den siebzehn
übrigen sind sechs Verweise (`DOC-8 = MNT-5`, `API-4 = SEC-8`, `DEP-3 = OPS-2`)
oder ausdrücklich positive Feststellungen (SEC-9, OPS-6, ARC-4 teilweise). Die
restlichen elf standen in keiner Phase — niemand hätte sie je angesehen.

Nachgemessen am 08.09.2026, mit Ausführung statt mit Mustersuche: **drei sind
zu** (PRF-1 über SEC-2, TST-2 über COR-1, TST-5), **acht sind offen**. Der
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
  Zwei Stellen fragten nicht nach dem Typ. Beim Nachmessen **drei** weitere
  `gather`-Stellen geprüft und bewusst nicht geändert: `fields.py` wärmt nur
  vor und verwirft begründet, `skills.py` und `flows/tree.py` tragen die
  Regel seit Schritt 14 bzw. COR-2 in einer engeren Form. Mein erstes
  Suchmuster hatte sie fälschlich gemeldet.

  Nachgezählt bei der Prüfung am 09.09.2026: die Regel steht damit an
  **sechs** Stellen. Die Commit-Nachricht `179243a` sagt „alle vier" und
  „zwei weitere geprüft" — beides zu niedrig; sie ist gepusht und bleibt,
  hier steht die Zahl richtig.

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

- [x] **29 · Prüfungsnachlese** Fünf Commits, `94866a3` … `fabd995`.

  **Der MAJOR traf wieder meine eigene Nachlese.** `_count` fiel bei fehlender
  Gesamtzahl auf `list()` zurück — und `list()` filtert auf den Aspekt, während
  `pagination.total` **jedes** Kind zählt. Zwei Pfade, zwei Zahlen für denselben
  Knoten, und die kleinere traf eine belegte Position. Belegt mit einem Anhang
  auf Position 1 plus einer Version: mit Gesamtzahl wurde 2 vergeben, ohne sie
  1. Der Test dafür konnte es nicht sehen, weil seine beiden Kinder **beide**
  den Aspekt trugen — der Gegentest daneben benutzt ausdrücklich eines ohne.
  Genau diese Asymmetrie war die Lücke.

  **Eine Verwechslung, die fünfmal dastand.** Ich hatte behauptet, COR-11
  träfe nur die weggelassene Eigenschaft — „als leere Liste zurückgegeben
  stimmte der Vergleich schon". `[""]` ist aber eine Liste **mit** leerem
  Eintrag; die leere Liste ist `[]`, und `first([])` gibt `None`. Es waren
  **zwei** von drei Formen kaputt, und die eine, die stimmte, hatte ich falsch
  benannt. Die Attrappe baute genau die eine, sodass `[]` nirgends geprüft war.

  **Zwei Wachen, die nicht wachten.** Die COR-7-Live-Tests liefen mit der
  Rückleseprobe, und die erzwingt über `check()` genau die Gleichheit, die der
  Test danach zusichert — ein umsortierender Server wäre rot geworden, aber als
  `SilentDropError`, nie mit der Erklärung. Und der Deckel auf den
  Untersammlungen hing an nichts: `maxItems` entfernen ließ die **ganze** Suite
  grün, `collections_truncated` wäre für immer `False`.

  Der erste Anlauf mit `verify=False` allein war halb — ohne Probe gibt
  `update` den Knoten von *vor* dem Schreiben zurück. Beide Tests wurden rot
  mit `[]`, und erst das Ausführen zeigte es.

  **Die Begründung für COR-9 überzeichnete.** „Aus 0 Bytes wird keine Größe bei
  `cclom:size`" kann in der Form, die edu-sharing sendet (`["0"]`), nicht
  eintreten — dort griff schon der Listenzweig. Der Grund bleibt, aber er ist
  ein anderer: das Sicherheitsnetz hatte eine andere Regel als die, die
  `flows/serialize.py` für dieselbe Frage aufschreibt.

  **Einem Befund halb widersprochen.** „`content.hash` gibt es nicht" stimmt
  für ein Attribut von `NodeContent`, aber die Schreibweise bezeichnet an vier
  weiteren Stellen das Antwortfeld `raw["content"]["hash"]` und ist dort die
  Konvention des Projekts.

Damit ist der Bericht abgearbeitet und zweimal nachgeprüft.
