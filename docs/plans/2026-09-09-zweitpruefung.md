# Zweitprüfung vom 09.09.2026 — die zehn Restbefunde

Quelle: die zweite Runde desselben Prüfers, über Commit `ed1f575` — den Stand,
den die erste Runde erzeugt hat. Sie bestätigt **alle 15 F-Befunde als
behoben** und meldet zehn neue Befundgruppen `R01`–`R10`.

**Alle zehn treffen zu.** Nachgestellt mit 16 Messungen in
`scratchpad/nachstellung_zweitpruefung.py`, jede unter der genannten Bedingung
und mit der dort behaupteten Beobachtung als Zusicherung; alle grün, im ersten
Anlauf. Diesmal war keine meiner Nachstellungen falsch gebaut.

## Vier Dinge, die der Bericht nicht sagt

1. **R04 ist eine Regression, die ich selbst eingeführt habe.** Vor der
   F09-Korrektur gab `CuratedPage.rendered` bei einer gekürzten Liste die
   erste geladene Variante zurück; `flows.page()` zeigte also *etwas*.
   Seit F09 ist `rendered` dort `None` — und `_choose()` kennt nur einen Grund
   dafür: „dieser Ordner hat keine Varianten". Aus einer stillen Falschaussage
   wurde eine laute. Besser, aber nicht richtig, und es ist meine Zeile.

2. **R03 ist die Kehrseite meiner eigenen F04-Entscheidung.** Ich habe
   `_not_stored` bewusst nur an `revoke` gehängt und im Commit „Scope" dazu
   gesagt. Der Prüfer hat die Gegenprobe gemacht, die ich nicht gemacht habe:
   `grant` sendet ebenfalls die **ganze** lokale ACL, verliert also genauso
   fremde Einträge und die Vererbung. Die Begründung „kleinster Eingriff" war
   hier die falsche.

3. **R09 ist eine Folge der F10-Korrektur.** Die alte, rohe
   Zeichenkettenprüfung war für Pfad-Gleichheit falsch, konnte aber an keinem
   Kandidaten scheitern. `urlsplit` kann. Ein Fix, der eine neue Fehlerart
   einführt, ist kein halber Fix — aber er gehört zu Ende gebracht.

4. **R10 hat keine Stelle, an der man ihn klein beheben könnte.** Gemessen:
   **kein** handgeschriebenes Modul importiert `_generated`. Die Bibliothek
   umhüllt diese Schicht nicht, sie erreicht sie nicht, und es gibt keine
   Grenze, an der eine Prüfung sitzen könnte. Siehe „Zu entscheiden".

## Regeln

Wie in der ersten Runde: **Test zuerst**, ein Commit je Befund, vor jedem
Commit ruff, `mypy --strict` und die ganze Suite mit direkt gelesenem
Exit-Code. Jede neue Wache durch Mutation belegt. Die Nachstellungen wandern
als Regressionstests in die Testdatei ihres Moduls.

## A · Identität und Rechte

- [ ] **1 · R01** Ein eingebrachter Client mit vorhandenen Cookies wird
      abgelehnt. Die Politik aus F01 verhindert das **Speichern**; einen schon
      gefüllten Speicher leert sie nicht, und httpx kopiert ihn beim Bauen der
      Anfrage in einen neuen Speicher ohne diese Politik. Gemessen ging
      `JSESSIONID=preexisting-dummy` an die ausdrücklich anonyme Anfrage *und*
      an `cdn.example.test`. Dieselbe Entscheidung wie bei F02: ablehnen, nicht
      filtern. Pro Anfrage am gemeinsamen Speicher zu löschen ist unter
      Parallelität keine Lösung.
      **Wache:** frischer und vorgefüllter Client, Cookie mit und ohne
      Domain/Pfad, anonym/Bob/externer Download. **Gegenprobe:** eine als
      `Credential` konfigurierte Cookie-Anmeldung geht weiterhin mit.

- [ ] **2 · R02** `unpublish()` prüft die Nachbedingung, nicht nur die
      Vorbedingung. Die Prüfung auf geerbte öffentliche Rechte läuft heute
      **vor** `revoke()`; kommen sie während des Schreibens dazu, steht das
      schon im Rücklesen, und trotzdem kommt `True` zurück. `revoke` liest
      bereits zurück — das Ergebnis muss `unpublish` erreichen, statt eine
      dritte Anfrage zu kosten.
      **Wache:** geerbte Rechte, die vor, während und nach dem POST dazukommen.

- [ ] **3 · R03** `grant()` prüft dieselben drei Dinge wie `revoke()`. Der
      POST ersetzt die ganze lokale Liste, also verliert `grant` genauso
      fremde Einträge und die Vererbung. Gemessen: `grant=True`, Alice weg,
      `inherits=False` trotz gesendetem `True`. Der Vergleich wird geteilt,
      nicht kopiert.
      **Wache:** verlorener fremder Eintrag und gekippte Vererbung, je einzeln
      mutiert. **Gegenprobe:** die gemessene stille Verwerfung eines
      unbekannten `GROUP_`-Namens meldet weiterhin ihre eigene Meldung.

## B · Vollständigkeit über die Schichten

- [ ] **4 · R04** `flows.page()` reicht die Abschneidung durch. Drei Zustände
      werden unterschieden, die heute alle „keine Varianten" heißen: der
      Ordner hat wirklich keine, die festgelegte ist nicht gelesen, und eine
      ausdrücklich gewünschte ist nicht gelesen. `truncated` bekommt wie in
      `search_in_collection` einen Grund.
      **Wache:** der 51-Varianten-Fall **über `repo.flows.page()`**,
      einschließlich `variant="v50"`.

- [ ] **5 · R05** Der Gang durch den Sammlungsgraphen wird breitensuchend.
      Heute markiert eine Tiefensuche eine Sammlung als gesehen, die sie über
      den *längeren* Weg zuerst erreicht — der kürzere Weg wird danach
      übersprungen, und was dahinter liegt, fehlt. Gemessen entscheidet die
      Reihenfolge der Serverantwort über den Treffer, beide Male mit
      `truncated=False`. Breitensuche erreicht jede Sammlung zuerst über den
      kürzesten Weg; damit ist `seen` wieder richtig, jede Sammlung erscheint
      genau einmal, und der Deckel zählt sie einmal.
      **Wache:** beide Reihenfolgen ergeben dieselbe Menge; dazu Diamant,
      Zyklus und Deckel. **Der Materialschnitt aus F08 bleibt.**

- [ ] **6 · R06** Die Facetten behalten Restanzahl und Abschneidung.
      `Facet.other_count` und `Facet.truncated` gibt es im Modell und fallen
      in `_facet_values` heraus. Ergänzt wird ein Geschwisterschlüssel
      `facet_meta`, wie `truncated_by` und `collections_truncated` es in
      dieser Bibliothek schon tun — die Werteliste unter `facets` bleibt, wie
      sie dokumentiert ist.
      **Wache:** die Kette Antwort → Modell → Flow → `search_all`.

- [ ] **7 · R07** `flows.text()` übernimmt die Quell-URL, sobald sie gelesen
      ist. Sie wird heute erst hinter dem frühen Rückgabepfad zugewiesen, also
      fehlt sie genau dann, wenn der Text aus dem Repositorium kam — der
      häufigste Fall. Die Docstring verspricht sie „whenever there is one".
      **Wache:** Repository-Text, Download und Extraktion tragen dieselbe URL.

- [ ] **8 · R08** `related()` schließt das eigene Original aus. Verglichen
      wird heute nur die übergebene ID; `describe()` hat die Original-ID
      daneben schon aufgelöst, und `SearchHit` trägt sie ebenfalls. Aus einer
      Sammlungsansicht heraus empfiehlt „Ähnliches" sonst dasselbe Material.
      **Wache:** Aufruf mit Original und mit Referenz ergibt dieselbe Menge.
      **Gegenprobe:** Treffer ohne `originalId` bleiben brauchbar.

- [ ] **9 · R09** Ein unlesbarer Kandidat bricht die Dublettenprüfung nicht
      ab. `_comparable` ruft `urlsplit` ohne Behandlung; eine fremde
      gespeicherte `ccm:wwwurl` muss nicht syntaktisch gültig sein. Gemessen:
      `ValueError: Invalid IPv6 URL` — keine Bibliotheksausnahme. Ein
      Kandidat, dessen Adresse nicht lesbar ist, ist nicht dieselbe Adresse
      wie eine gültige; er wird übersprungen. Eine **eigene** ungültige
      Adresse bleibt ein `ValidationError`.
      **Wache:** kaputter Kandidat neben gültigem Treffer; kaputte eigene
      Adresse.

## C · Die generierte Schicht

- [ ] **10 · R10** Die Grenze wird benannt und gepinnt, nicht behoben. Siehe
      „Zu entscheiden": ohne eine vendorte Generatorvorlage gibt es keine
      Stelle dafür. Der gemessene Zustand bekommt eine Wache, damit er eine
      bekannte Eigenschaft mit Besitzer ist und keine Überraschung.

## Zu entscheiden

**R10 — 160 Zeilen Jinja vendorn?** Der Generator nimmt
`--custom-template-path`. Gebraucht würde `endpoint_module.py.jinja`, 160
Zeilen, von denen **eine** zu ändern wäre:

```jinja
{{parameter.python_name}}=quote(str({{parameter.python_name}}), safe=""),
```

Dagegen spricht: die Kopie muss der Generatorfassung folgen, und sie beträfe
die Erzeugung aller 389 Endpunkte, um eine Schicht abzusichern, die diese
Bibliothek selbst nicht benutzt — gemessen importiert kein handgeschriebenes
Modul `_generated`. Dafür spricht: das CI-Gate erzeugt bei jedem Push neu,
eine veraltete Vorlage fiele also sofort als Diff auf.

Empfehlung: **vorerst nicht vendorn.** Die Komfortschicht lehnt die Werte ab,
die Grenze steht seit F07 in `path_segment` und in REFERENCE, und eine Wache
hält den gemessenen Zustand fest. Wer die generierte Schicht direkt benutzt,
arbeitet ohnehin ohne die Zusagen dieser Bibliothek. Eine Gegenmeinung ist
gut vertretbar — dann ist es ein eigener Schritt mit eigenem Commit.

## Nicht Teil dieser Runde

Abschnitte 5 und 6 des Berichts (acht neue Flow-Entwürfe und ein gemeinsamer
Ablaufkern) sind Bau, nicht Reparatur. Der Bericht sagt selbst, sie sollten
auf den geschlossenen Verträgen aufsetzen — also nach A bis C, als eigene
Entscheidung.

Ebenso offen bleibt die **Live-Verifikation der Rechtefälle** aus der ersten
Runde: R02 und R03 vergrößern sie, sie bleibt aber dieselbe Aufgabe.
