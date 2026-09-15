# Drittprüfung vom 10.09.2026 — Plan

Der Bericht prüft `4b6ec40` und bestätigt: **F01–F15 halten, R01–R09 sind
behoben.** Er meldet vier offene Befundgruppen — `A01`, `A02`, `R10`, `D01` —
und schlägt in Abschnitt 5 acht Funktionserweiterungen `U1`–`U8` vor, die er
selbst als *nicht implementiert* kennzeichnet.

## Was ich nachgemessen habe, bevor ich etwas anfasse

Jeder Befund wurde nachgestellt. Nicht gelesen — ausgeführt.

| Befund | Nachstellung | Ergebnis |
|---|---|---|
| A01 | Server speichert für Alice nur `Write`, wirft ihr `Read` weg; Bob und Vererbung unverändert | `grant()` → **`True`**. Gesendet `['Read', 'Write']`, zurückgelesen `['Write']`. **Reproduziert.** |
| A02 | `https://alice:DUMMY_AUDIT_PASSWORD@[broken` durch `find_by_url` und `check_before_create` | Passwort im `ValidationError`, in `warnings` **und** im `ConflictError`. **Reproduziert — und breiter als gemeldet:** derselbe Klartext steht auch im Pfad „kein http(s)" (`ftp://alice:…@host/x`), also an sechs Stellen statt drei. |
| R10 | `_get_kwargs(repository="-home-", node=".")`, nur Request gebaut | `.` → `/nodes/-home-`, `..` → `/nodes`. Komfortschicht lehnt beide mit `EduSharingError` ab, nimmt `id.mit.punkten`. **Reproduziert, Zustand unverändert.** |
| D01a | `unpublish()`-Docstring gegen den Ablauf | „Nothing is written when this is raised" gilt nur für den Konflikt **vor** dem Schreiben. Der R02-Pfad wirft **nach** `_revoke`. **Belegt.** |
| D01b | `browse_tree()`-Docstring gegen die Implementierung | Docstring sagt „depth-first", die Implementierung ist `deque` + `popleft()` = Breitensuche, und der innere Kommentar sagt das auch. **Belegt.** |

## Reihe A · Was repariert wird

- [x] **A01 · `grant()` prüft den ganzen zusammengeführten Eintrag.**
      Heute prüft der erste Vergleich nur `wanted`, und `_not_kept(…,
      skip=authority)` lässt die bearbeitete Autorität aus — zwischen beiden
      fällt ihr Altbestand durch. Die Korrektur braucht **keinen** zusätzlichen
      HTTP-Aufruf: `after` ist bereits gelesen. Eigener Fehlertext, weil der
      Grund ein anderer ist als beim unbekannten Gruppennamen.
- [x] **A02 · Jede diagnostische URL-Wiedergabe in `flows/duplicates.py`
      maskiert.** `mask_userinfo()` existiert seit F06 in `urls.py` und wird
      hier nicht benutzt. Betroffen: beide `raise`-Stellen in `find_by_url`,
      die `ConflictError`-Meldung und die Warnung in `check_before_create`.
      Vergleichsschlüssel und Such-URL bleiben unverändert — maskiert wird die
      *Meldung*, nicht die Abfrage.
- [x] **D01a · `unpublish()`-Docstring.** Zwei Zeitpunkte, zwei Zusagen: vor
      dem Schreiben ist nichts geschrieben, nach dem Schreiben ist der lokale
      Eintrag weg. Der Aufrufer entscheidet danach anders.
- [x] **D01b · `browse_tree()`-Docstring.** „depth-first" → Breitensuche, mit
      dem Grund, den R05 erzwungen hat: der kürzeste Weg zuerst macht `seen`
      wieder richtig.

## Reihe B · Was präzisiert wird

- [x] **Das Projekt-Audit sagt „15 + 10 findings" pauschal geschlossen.** R10
      ist es nicht — bewusst nicht. Der Satz bekommt die Ausnahme.
- [x] **Changelog.** Die beiden Reparaturen sind nutzersichtbares Verhalten.

## Was diese Runde nicht ist

- **R10 bleibt eine Entscheidung, keine Reparatur.** Der Bericht lässt beides
  zu: „ausdrücklich als Grenze behandeln **oder** im Generator beheben". Die
  Grenze ist behandelt — vier Wachen halten sie fest, `path_segment` weist die
  Werte ab, beide REFERENCE-Fassungen sagen es. Die Gegenrechnung steht in
  `2026-09-09-zweitpruefung.md`: 160 Zeilen Jinja vendorn, um eine Zeile zu
  ändern, für eine Schicht, die kein handgeschriebenes Modul importiert. Die
  Entscheidung ändert sich, wenn diese letzte Wache fällt.
- **Abschnitt 5 (`U1`–`U8`) ist Bau, nicht Reparatur.** Der Bericht sagt es
  selbst, und er sagt auch, worauf sie aufsetzen sollen (`U1` und `U8` als
  gemeinsame Grundlage). Das ist eine Produktentscheidung, kein Prüfbefund.

  **Eine Ausnahme, und sie ist scharf begrenzt.** In `U2` steckt neben dem
  Vorschlag eine Tatsachenbehauptung, und die habe ich nachgemessen: bei
  `limit=2` holt `related()` drei Kandidaten, und sind das das Original und
  zwei Referenzen darauf, kommt `hits: []` mit `reason: ""` zurück. Das ist
  genau das, was dieses Paket sonst nirgends durchgehen lässt — `flows/tree.py`
  schreibt es als Prinzip auf: „a caller cannot tell an empty result from an
  unfinished one". Das Feld `reason` gibt es bereits und der Nachbarzweig
  benutzt es genau dafür. Also: **Grund nennen — ja**, das ist Reparatur eines
  stummen Ergebnisses. **Nachladen, bis genug fremde Originale da sind — nein**,
  das ist eine neue Zusage und damit Bau.
- **Die Live-Abnahme** bleibt offen, aber ein Stück kleiner. Der
  A01-Kontrollfall ist jetzt an der Instanz belegt (siehe Ergebnis); die
  *Fehler*fälle R02, R03 und A01 bleiben am Modell, weil sie einen Server
  verlangen, der falsch antwortet — den kann man nicht bestellen. Der
  Download-403 bleibt, wie der Bericht ihn einordnet: *nicht selbst
  verifizierte Betriebsfrage*, und er braucht Rechte auf der Instanz, keinen
  Code.

## Vorgehen

Test zuerst, und jede Wache durch Mutation belegt: die neue Prüfung wird
abgeschaltet, der Test muss rot werden. Daneben die Gegenproben, damit kein
Fix grün wird, indem er alles ablehnt. Vor jedem Commit `ruff check .`,
`mypy --strict` und die ganze Suite.

## Ergebnis

Vier Commits nach dem Plan, `e0a4dfa` bis `64caba4` und der Nachtrag. Vor jedem
`ruff check .`, `mypy --strict` und die ganze Suite — Exit-Code gelesen, nicht
vermutet.

| Schritt | Beleg |
|---|---|
| A01 | Test vor der Reparatur rot („DID NOT RAISE"), danach grün. Mutation `gone = []`: **genau dieser** Test fällt, die 43 anderen bleiben grün. Drei Gegenproben. |
| A02 | Fünf Tests vor der Reparatur rot, zwei Gegenproben vorher wie nachher grün. Mutation `mask_userinfo` als Identität: genau die fünf fallen. |
| D01 | Keine neuen Tests — das Verhalten ist gepinnt, veraltet war die Beschreibung. Belegt am Quelltext (`deque`/`popleft`; der zweite `ConflictError` nach `_revoke`). |
| Suite | 2232 → 2239 bestanden, 9 übersprungen. Ruff und `mypy --strict` sauber. |
| Live | Schreibsuite gegen Staging: 62 bestanden, 3 gescheitert — dieselben drei Download-403 wie vor der Runde, keine Regression. |
| U2 (halb) | Test vor dem Fix rot („eine leere Antwort ohne Grund"), danach grün. Mutation `if False`: genau dieser Test fällt. Zwei Gegenproben — eine gefüllte Antwort bekommt keinen Grund, und eine Suche ohne Treffer bekommt nicht den *Filter*grund, weil sie aus einem anderen Grund leer ist. |
| Live · A01 | Der Kontrollfall des Berichts an der Instanz statt am Modell: `grant("Consumer")`, dann `grant("Coordinator")` derselben Autorität → gespeichert ist `['Consumer', 'Coordinator']`, exakt beide Namen. Das war die **einzige** Art, wie diese Reparatur hätte schaden können — fasste die Instanz Rollen zusammen, würde ein berechtigter grant jetzt werfen. Tut sie nicht. Als Test drin, nicht als Notiz. |

**Was der Bericht über diese Bibliothek hinaus sagt.** A01 war kein
übersehener Randfall, sondern eine Zusage ohne Prüfung dahinter: „permissions
this authority already holds are kept" stand seit jeher in der Docstring, und
kein Test hat je danach gefragt. Die Werkzeuge, mit denen das
Finalisierungs-Audit gemessen hat — `mypy --strict`, `pip-audit`, Coverage,
grüne Suite — können so etwas nicht finden. Nur der Abgleich *Zusage gegen
Test* findet es. Für die nächste Runde ist das der Griff: jede Zusage einer
öffentlichen Docstring gegen den Test suchen, der sie hält.

## Nachtrag · Review der eigenen Runde

`better-coding-review` über `4b6ec40..c388778`. Ein echter Fehler, und er saß
ausgerechnet in der Reparatur, die diese Runde *freiwillig* mitgenommen hat.

**Befund 1 · `related()` erfand einen Grund.** `hits` entsteht als
`[gefiltert][:limit]`, und die neue Erklärung hing an `hits`. Bei `limit=0`
schneidet das Limit alles ab, auch wenn der R08-Filter nichts genommen hat —
und der Text behauptete trotzdem „every one of them was this material itself
or a reference to it". Gemessen mit zwei völlig fremden Treffern: beide
Hälften des Satzes falsch, die Zahl kam von `limit + 1`.

Die Reparatur trennt die zwei Schritte (`kept` vor `hits`) und fragt den
Grund von `kept`. Test vorher rot, Mutation zurück auf `hits` macht genau ihn
rot. Dazu die Gegenprobe, dass ein *echter* Filtergrund auch bei `limit=0`
noch genannt wird — sonst wäre die Reparatur grün, indem sie schweigt.

Daran hing ein zweiter Fund, den erst der Fix sichtbar machte: die Docstring
sagte, `reason` erkläre *jedes* leere `hits`. Nach der Reparatur stimmt das
absichtlich nicht mehr. Sie sagt es jetzt genau: erklärt wird, was der
Aufrufer nicht sehen kann; ein selbstgesetztes `limit` gehört nicht dazu.

**Befund 2 · `publish()` hatte keinen `Raises:`-Abschnitt.** Es ist ein
`grant` an `GROUP_EVERYONE` und erbt jeden Weg, auf dem der schiefgehen kann —
seit A01 einen mehr. Vorbestehende Lücke, die diese Runde wahrscheinlicher
gemacht hat.

**Vier Kosmetika.** Verlorene Backticks in einem Kommentarblock (mein
Patch-Skript hatte sie beim Shell-Escaping verschluckt), ein ungleichmäßiger
Umbruch, ein Tippfehler — und ein Test-Double, dessen Docstring von „der
bearbeiteten Autorität" sprach, während der Code hart `alice` umschrieb. Das
Double ist jetzt generisch und modelliert, was es behauptet; die Beweiskraft
des Tests wurde danach neu belegt.

**Die Lehre dieser Runde, zum zweiten Mal.** A01 war eine Zusage ohne Test.
Befund 1 war eine Zusage, die ich in derselben Runde neu aufgestellt und selbst
nicht durchgeprüft habe — der Grund war für den Normalfall richtig und für den
Randfall erfunden. Wer eine Erklärung ausgibt, schuldet ihr denselben Beweis
wie einer Wache.

## Nachtrag 2 · Die Download-Abnahme, die noch fehlte

Beim Durchgehen der offenen Punkte fiel auf, dass ich Abschnitt 2 des Berichts
nur halb erfüllt hatte. Er verlangt für den Download **„ein bekanntes, lesbares
Testdokument"** — ich hatte ausschließlich *selbst hochgeladene* Knoten
gemessen und daraus geschlossen, das Servlet ehre Basic-Auth „for this account"
nicht. Eine Verallgemeinerung aus einer Stichprobe, und sie war falsch.

| Probe | Ergebnis |
|---|---|
| fremdes, öffentliches Dokument, anonym | Metadaten, `text()`, `download()` — alles ok, 5 867 B |
| dasselbe mit unseren Zugangsdaten | identisch, 5 867 B |
| eigener **privater** Upload, angemeldet | `403`, auch nach 69 s — keine Verzögerung |
| `text()` auf demselben privaten Knoten | ok, 25 Zeichen |
| derselbe Knoten nach `publish()` | `download()` liefert — **und anonym ebenso** |

Das Servlet authentifiziert **gar nicht**. Es liefert öffentlich Lesbares und
verweigert alles andere, egal wer fragt. Damit erklärt sich auch die ältere
Messung, dass ein anonymer und ein Basic-authentifizierter Aufruf byteweise
dieselbe 403-Antwort bekommen: für das Servlet sind sie derselbe Aufruf. Die
Rechte des Kontos waren nie die Frage.

**Und es war nicht immer so.** Die Zeile `assert await node.content.download()
== inhalt` auf einem privaten Knoten stammt aus `0aef368` vom 27.08.2026, und
Zusicherungen werden hier gemessen. Die Instanz hat sich in vierzehn Tagen
geändert — das gehört an die, die sie betreiben, und ist eine andere Auskunft
als „dem Konto fehlt ein Recht".

Was daran Reparatur war: der **Aufrufer** erfuhr nichts. Wer eine Datei
hochlädt und zurückliest, bekam `PermissionDeniedError` ohne Erklärung.
Docstring und beide REFERENCE-Tabellen nennen die Grenze jetzt und verweisen
auf `text()`. Die drei roten Live-Tests bleiben rot — sie prüfen richtiges,
gewünschtes Verhalten, und grün zu machen hieße, die Instanzgrenze als
Bibliothekszusage festzuschreiben. Dazu ein Charakterisierungstest, der die
drei Messungen gegeneinander pinnt.

**Dieselbe Lehre, zum dritten Mal.** A01 war eine Zusage ohne Test. Befund 1
des Reviews war eine Erklärung ohne Beweis für den Randfall. Und dies war eine
Ursachenaussage, die aus einer einzigen Art von Knoten verallgemeinert hat.
Dreimal dasselbe Muster: nicht das Messen fehlte, sondern das Prüfen der
Gegenhypothese.

## Nachtrag 3 · Die Abnahmen, Kriterium für Kriterium

Der Bericht nennt zu jedem Befund eine eigene Abnahme. Bisher hatte ich sie
erfüllt, aber nirgends gegeneinander gestellt. Hier steht jedes Kriterium mit
dem Test, der es hält — 19 offline, 3 live, alle grün.

### A01 — „Ergänzung bei derselben Autorität mit Verlust eines alten Rechts muss `SilentDropError` erzeugen. Die Kontrollfälle … müssen ihre jeweiligen richtigen Ergebnisse behalten."

| Kriterium | Test |
|---|---|
| Verlust eines alten Rechts → `SilentDropError` | `test_grant_bemerkt_den_verlust_alter_rechte_derselben_autoritaet` |
| „alte und neue Rechte erhalten" | `test_ein_grant_der_alte_und_neue_rechte_behaelt_meldet_true` |
| „fremder Eintrag verloren" | `test_grant_bemerkt_den_verlust_fremder_eintraege` |
| „Vererbung verändert" | dasselbe, plus `test_revoke_meldet_wenn_die_vererbung_umgeworfen_wird` |
| an der Instanz statt am Modell | `test_ein_zweiter_grant_behaelt_das_erste_recht` (live) |

„Vererbung verändert" fällt im Grant-Test mit „fremder Eintrag verloren"
zusammen — ob sie eigenständig bewacht ist, klärt nur die Mutation. Mit
abgeschalteter Vererbungsprüfung fallen **drei** Tests, darunter ein eigener
für `revoke`; und `_not_kept` ist für `grant` und `revoke` dieselbe Funktion.
Belegt.

### A02 — „Ein eindeutiger Dummy-Geheimniswert darf weder in `str(exception)` noch in den Warnungen beider Erstellungsmodi stehen. Derselbe Test soll gültige und nicht parsebare URLs mit Benutzerinformationen abdecken."

| Kriterium | Test |
|---|---|
| nicht in `str(exception)` | `test_eine_unlesbare_eigene_adresse_zeigt_kein_passwort`, `…ohne_http_schema…` |
| nicht in den Warnungen (`if_exists="return"`) | `test_die_uebersprungene_pruefung_warnt_ohne_passwort` |
| nicht im `ConflictError` (`if_exists="raise"`) | `test_die_ausgefallene_pruefung_wirft_ohne_passwort`, `…gefundene_dublette…` |
| **gültige** URL mit Benutzerinformationen | `test_die_gefundene_dublette_meldet_ohne_passwort` |
| **nicht parsebare** URL mit Benutzerinformationen | `test_eine_unlesbare_eigene_adresse_zeigt_kein_passwort` |

Zwei Datenpfade führen das Geheimnis weiter, und beide **bleiben so**: das Feld
`existing["url"]` gibt die gespeicherte Adresse wörtlich zurück, und
`add_material` schreibt die übergebene Adresse wörtlich als `ccm:wwwurl`. Der
Bericht nimmt beides ausdrücklich aus („Der Vergleichsschlüssel und die
eigentliche Metadaten-URL brauchen dafür nicht verändert zu werden"; „Ob URLs
mit Zugangsdaten als Materialquelle grundsätzlich erlaubt sein sollen, ist eine
eigene API-Entscheidung"). Maskieren würde das Vergleichsfeld unbrauchbar
machen. Beides ist jetzt im Docstring gesagt, statt still zu sein.

### D01, R10, Download

| Kriterium | Beleg |
|---|---|
| Docstrings beschreiben den tatsächlichen Ablauf | Abgleich mit den vorhandenen Verhaltensprüfungen (`test_flows_tree.py`, beide `unpublish`-Konflikte) |
| R10-Grenze bleibt eindeutig | vier Wachen in `test_generated_layer.py`, alle grün |
| Rechtepfad hat einen Instanztest | `test_ein_zweiter_grant_behaelt_das_erste_recht` (live) |
| Dateipfad hat einen Instanztest | `test_das_download_servlet_liefert_nur_oeffentliches` (live) |

### Werkzeuge

`pip-audit` gegen die Laufzeitabhängigkeiten (`httpx>=0.27`, `attrs>=23.2`) und
gegen die ganze Umgebung: **No known vulnerabilities found**. Beim vollen Lauf
wird nur das lokale Paket selbst übersprungen — es liegt nicht auf PyPI.
