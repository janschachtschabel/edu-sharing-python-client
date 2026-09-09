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

- [x] **30 · Dritte Prüfung** Acht Commits, `f4e626a` … `b1273a2`. Anlass war
  gemessen: **beide MAJOR dieser Sitzung steckten in einer Nachbesserung, nicht
  im ursprünglichen Fix.** Also wurden die Nachbesserungen geprüft.

  **Kein MAJOR.** Die Kette an `_count` — dreimal umgebaut — ist zur Ruhe
  gekommen; die Matrix aus Serverantworten liefert überall dieselbe Zahl auf
  beiden Wegen, und die beiden Regressionen werden durch Mutation weiterhin rot.

  **Der eine Fund, der Code betraf, war die Zusage selbst.** `add()` sagt
  *hinter den bestehenden* und nahm die **Anzahl** der Kinder — was dasselbe
  nur sagt, solange die Nummern lückenlos bei 0 beginnen. Gemessen: zwei
  Anhänge mit `order=` auf 5 und 6, der nächste bekam 2 und stand in `list()`
  **zuerst**. Audit MNT-4 hat genau diese Bauform vorgeschrieben („order from a
  `limit=1` page's total"); der Befund selbst — der stille Deckel — bleibt
  behoben, die Nebenvorschrift ist gegen die Messung revidiert. Aus `_count`
  wurde `_next_position`, und die Zweipfad-Struktur, aus der beide MAJOR kamen,
  fällt damit weg.

  **Zwei Rücknahmen kamen nicht überall an.** Die COR-11- und die
  COR-9-Berichtigung standen im Code, aber nicht in den Statusabsätzen des
  Audits — und `c2a95ff` hatte gerade einen Kopfhinweis gesetzt, der Leser
  ausdrücklich auf diese Absätze als aktuellen Stand verweist.

  **Und drei eigene Funde vorweg**, bevor die Prüfung zurückkam: `94866a3`
  legte eine dritte Kopie derselben Attrappe an, unter ihren Nutzern; die
  Dokumente beschrieben `add()` noch nach dem Stand davor; und meine eigene
  Berichtigung dazu setzte die Deckelgrenze eins zu hoch.

  Zwei Zahlenbehauptungen wurden nachgeprüft und halten: die Teilantwort-Regel
  steht an **sechs** Stellen, und vom Kopfhinweis bis zum ersten Statusabsatz
  sind es 96 Zeilen — „rund hundert".

- [x] **31 · Die offenen Dinge** Zwei Punkte hatte ich in Runde 30 benannt
  und liegengelassen; beide sind zu.

  **Der Ausnahmeschlüssel nennt die Stelle vollständig.** Der blanke
  Funktionsname ließ eine gleichnamige Funktion auf Modulebene die Ausnahme
  erben — und beide Wächter blieben dabei grün. Mit `Skills.registry` statt
  `registry` schlagen jetzt beide an.

  **Und der Deckel wird gemessen statt geraten.** Ich hatte geschrieben, ein
  Server, der die Seitengröße als `total` meldet, sei „prinzipiell nicht
  erkennbar". Das stimmte nicht: man kann einen Datensatz **mehr** anfordern
  als der Deckel nimmt, und was ankommt, sagt es — ohne jede Gesamtzahl.
  Live gemessen mit 205 Kindern in einem Wegwerf-Ordner: `maxItems=201`
  liefert 201 Datensätze. Damit fällt auch die falsche Ablehnung bei genau
  200 Kindern weg, die als bewusster Preis dabeistand.

Damit ist der Bericht abgearbeitet und dreimal nachgeprüft.

- [x] **32 · Ein Muster, sieben Stellen** Aus dem zweiten offenen Punkt wurde
  ein Zug. Die Frage „ist diese Seite alles?" stand an **sieben** Stellen und
  war überall aus `pagination.total` beantwortet — also „vollständig", wo
  keine Zahl genannt wird, und ebenso, wo eine genannte nicht größer ist als
  die Seite. `dto.page_cut` ist jetzt die eine Lesart; jede Stelle fragt einen
  Datensatz mehr, als sie ausliefert.

  **Drei Live-Messungen tragen das** (09.09.2026, edu-sharing 11.0, alles in
  selbst angelegten Wegwerf-Objekten, danach gelöscht): der Knoten-Endpunkt
  liefert auf `maxItems=201` **201** Datensätze von 205; der Sammlungs-Endpunkt
  beachtet `maxItems` genauso; und `pagination.total` **respektiert den
  Filter** — drei Dateien neben zwei Unterordnern ergeben bei `filter=files`
  `total: 3`, nicht 5. Erst das Letzte macht den Vergleich „genannte Zahl gegen
  Gezeigtes" zulässig, und der ist strenger als der gegen den Deckel.

  **Zwei eigene Fehler dabei gefunden.** Ich hatte `default=-1` als die
  verborgene Feinheit des Helfers bezeichnet — sie ist keine, `-1` und `0`
  liegen beide unter jedem Deckel. Und mein erster Helfer verglich gegen den
  Deckel statt gegen das Gezeigte, was in `skills_registry` eine Verschärfung
  zurückgenommen hätte: erschöpfend verglichen, 1326 Kombinationen.

  **Und eine Behauptung, die niemand gemessen hatte.** „`ngsearch` antwortet
  mit `pagination: null`" stand seit `ae05dcb` im Quelltext und wurde von dort
  in Kommentare, Tests und meine eigenen neuen Texte weitergetragen. Gemessen
  ist das Gegenteil: die Suche nennt `total: 1591`. Alle drei Endpunkte, die
  diese Bibliothek auflistet, nennen eine Zahl. Die Vorgabe in `page_total`
  bleibt — sie kostet nichts —, aber sie steht jetzt als **Vorsorge** da und
  nicht als Beobachtung. Der Eintrag 29 oben trägt den Satz noch; er ist die
  Aufzeichnung seines Tages und bleibt, wie er ist.

- [x] **33 · Selbstprüfung des Zuges** Fünf Commits, `8ff83ad` … `2fe1cfa`.
  Kein fremder Befund lag vor, also habe ich den eigenen Zug geprüft — dasselbe
  Vorgehen, das in dieser Sitzung zweimal die MAJOR fand.

  **Fünf Verweise zeigten ins Leere.** Der Zug löschte `_ist_gekuerzt` und
  benannte `_count` in `_next_position` um; die Verweise darauf blieben stehen,
  über vier Dateien. Keine der drei Doku-Wachen sah es — sie prüfen
  öffentliche Namen. Es gibt jetzt eine vierte, die das Umgekehrte fragt: zeigt
  das, was in einem Docstring **steht**, noch auf etwas?

  Einer der fünf war mehr als ein toter Name:
  `test_der_rueckfall_zaehlt_dasselbe_wie_die_gesamtzahl` hieß nach einer
  Bauform, die `_next_position` nicht mehr hat. Die Zusicherung darin gilt
  weiter, also heißt der Test jetzt danach.

  **Und die neue Wache hatte selbst zwei Löcher** — beide durch Mutation
  gefunden, keines durch Lesen: ihre Ausnahmen konnten verwaisen, und ihren
  Kernzweig abzuschalten ließ alles grün, weil es nach dem Aufräumen nichts
  mehr zu finden gab. Beide sind zu.

  **Dazu zwei kleinere.** `scan_truncated` versprach `(scanned, total)`, wo die
  zweite Zahl seit dem Umbau eine untere Schranke ist. Und die
  Eigenschaftswache für `page_cut` verspricht weniger, als es zunächst schien:
  unter einem Server, der `maxItems` beachtet, ist die Datensatz-Hälfte allein
  hinreichend — zwei von drei Mutationen kamen durch sie hindurch. Das steht
  jetzt in ihrem Docstring; eine Eigenschaft ist so stark wie ihre Annahme.
