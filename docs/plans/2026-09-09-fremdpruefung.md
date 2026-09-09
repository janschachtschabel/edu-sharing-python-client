# Fremdprüfung vom 09.09.2026 — die Befunde und der Weg, sie zu schließen

Quelle: ein Prüfbericht eines Dritten über Commit `57aaec7` — das ist `HEAD`.
Der Bericht nennt sich selbst eine Prüfung „eines etwas älteren Standes"; er
beschreibt den aktuellen. Jeder Befund ist also direkt nachstellbar, und genau
das ist zuerst passiert.

**Alle 15 Befunde treffen zu.** Dazu der statische Hinweis aus §5.2. Nachgestellt
wurde nicht durch Lesen, sondern mit **31 Messungen**, jede unter der im Bericht
genannten Bedingung und mit der dort behaupteten Beobachtung als Zusicherung.
Alle 31 sind grün, also ist jeder Befund reproduziert.

Zwei meiner ersten Nachstellungen waren falsch gebaut, nicht die Befunde:
`credential=None` heißt beim `Transport` „die eigene", nicht „anonym"; und mein
erstes Vierfach-Fence-Beispiel hatte eine *gerade* Zahl innerer Fences, wodurch
der Block verschluckt statt fälschlich erkannt wurde. Beides sagt dasselbe wie
so oft in diesem Projekt: eine Prüfung, die aus dem falschen Grund grün oder rot
ist, ist schlimmer als keine.

## Sieben Dinge, die der Bericht nicht sagt und die die Reihenfolge ändern

1. **F01 bricht eine Zusage, die dieses Repository selbst formuliert.**
   `auth.py` beginnt mit „Credentials are values, not global state. Every
   request gets its own. A service that serves many people — an MCP server, say
   — cannot otherwise keep straight who is asking." Genau das tut der
   Cookie-Speicher des geteilten `httpx.AsyncClient` zunichte. Gegengemessen:
   **kein Modul der Bibliothek liest oder setzt Cookies** — das automatische
   Mitführen ist niemandes Absicht, sondern httpx' Vorgabe.

2. **F02 macht eine dokumentierte Auskunft falsch.** `REFERENCE.md` führt
   `repo.raw.is_repository_url(url)` als „whether credentials would be
   attached". Mit einem eingebrachten Client, der Standard-Header trägt, ist
   diese Antwort unwahr — und `check_client()` prüft die Weiterleitung, aber
   nicht diese zweite Quelle. Gemessen: ein Client mit `Authorization` **und**
   ein Client mit `auth=` werden beide angenommen.

3. **F04 ist eine Lücke, keine Fehlvorstellung über den Server.** Gemessen:
   dieselbe stille Verwerfung meldet `grant()` korrekt als `SilentDropError`.
   Die Schwester tut es richtig, `revoke()` verwirft das Rücklesen, das
   `_write()` bereits ausführt. Der teure Teil — die zweite Anfrage — wird
   bezahlt und weggeworfen.

4. **F08 braucht kein neues Werkzeug.** `collection_contents` liefert
   `total_materials` und `returned_materials`; die Kürzung zeigt sich im
   Vergleich der beiden. Nachgemessen für den Fall, den die Abnahme von F08
   ausdrücklich verlangt: **auch ohne vom Server genannte Gesamtzahl** belegt
   der eine zusätzlich gelesene Datensatz die Kürzung. Der Fix ist Durchreichen,
   nicht Erfinden.

5. **F05 nimmt dem Schutz nichts.** Gegengemessen: ein entpackt zu großer Inhalt
   wird weiterhin korrekt mit `ContentTooLargeError` abgelehnt, obwohl seine
   komprimierte Größe unter der Grenze liegt. Kaputt ist allein der Erfolgsfall.
   Wer die Kodierung repariert, darf diese Wirkung nicht mitreparieren.

6. **F15 ist genauer, als der Bericht schreibt.** An der Referenzspezifikation
   ausgezählt: **sieben** Antworten tragen einen Inhaltstyp, den der Generator
   nicht übernimmt — sechsmal `application/text` am JWT-Endpunkt (200, 400, 401,
   403, 404, 500) und einmal `*/*` an `GET /ltiplatform/v13/content`. Davon sind
   **zwei Erfolgsantworten**. `docs/ARCHITECTURE.md` sagt: „Die einzige
   verbleibende Warnung: eine `500`-Antwort". Das ist messbar falsch, und es ist
   die Art Satz, die eine Prüfung beruhigt, statt sie zu leiten.

7. **F10 ist die einzige Ausnahme: keine Nachlässigkeit, sondern eine
   Entscheidung.** Das Modul dokumentiert sie — „the comparison ignores case and
   nothing else" — sie stammt gemessen vom MCP (`services/write/duplicates.ts`),
   und ein Test hält sie fest (`test_nur_die_gleiche_adresse_zaehlt` benutzt
   `URL.upper()` als Beispiel für „dieselbe Adresse"). Der Bericht hat trotzdem
   recht: ein Pfad ist nach RFC 3986 zeichengenau, `/A` und `/a` können zwei
   Seiten sein. Aber hier wird eine **Zusage geändert**, nicht ein Versehen
   behoben. Siehe „Zu entscheiden".

## Regeln für die Umsetzung

Wie in den Phasen 1–5: **Test zuerst**, ein Commit je Befund, vor jedem Commit
`scratchpad/gate.sh` (ruff, `mypy --strict`, ganze Suite) mit direkt gelesenem
Exit-Code. Dazu zwei, die dieser Runde eigen sind:

- **Jede neue Wache wird durch Mutation belegt** — Code oder Doku kaputtmachen,
  zusehen, wie der Test rot wird. Fünfmal in der letzten Runde hat das eine
  Wache entlarvt, die aus dem falschen Grund grün war; kein einziges Mal das
  Lesen.
- **Die 31 Nachstellungen wandern ins Repository**, jede in die Testdatei ihres
  Moduls, jede mit dem Befund im Docstring. Sie sind heute die Beschreibung
  eines Fehlers und ab dem Fix die Wache dagegen. Sie liegen bis dahin in
  `scratchpad/nachstellung_pruefbericht.py`.

## A · Identität und Rechte

- [ ] **1 · F01** Der Cookie-Speicher trägt keine Identität mehr über
      Anfragen. Der `Transport` baut seine Anfragen künftig ausdrücklich und
      entfernt den `Cookie`-Header, den httpx aus früheren Antworten ergänzt
      hat — für den selbst erzeugten wie für den eingebrachten Client, denn nur
      dann gilt die Zusage auch für den Fall, für den `credential=` gedacht ist.
      Eine Sitzung, die mitgehen *soll*, geht als `Credential` mit; dieser
      Erweiterungspunkt bleibt und wird dokumentiert.
      **Wache:** Alice → anonym → Bob, nacheinander *und* gleichzeitig; keine
      Anfrage trägt eine fremde Sitzung. **Mutation:** das Entfernen
      herausnehmen, Test muss rot werden.

- [ ] **2 · F02** Zugangsdaten eines eingebrachten Clients verlassen die
      Repositoriumsgrenze nicht. `check_client()` lehnt einen Client ab, der
      `auth=` oder einen Zugangs-Header als Vorgabe trägt, und sagt warum.
      Vollständig aufzählen lassen sich fremde Header **nicht** — darum ist die
      Ablehnung die Grenze und nicht ein Filter, der so tut als ob. Die
      Einschränkung gehört in REFERENCE und in die Docstring von
      `is_repository_url`, deren Auskunft dadurch erst wieder wahr wird.
      **Wache:** externer Download bekommt weder Standard-Header noch
      `client.auth` noch Sitzungscookie. **Mutation:** je Regel eine.

- [ ] **3 · F03** `unpublish()` fragt die richtige Frage. Der Konfliktschutz
      prüft heute, ob ein *eigener* Eintrag existiert; er muss prüfen, ob der
      Knoten **danach noch öffentlich** ist. Damit fallen die drei Fälle —
      nur eigen, nur geerbt, beides — von selbst auseinander, und der gemischte
      hört auf, durch die Lücke zwischen zweien zu fallen.
      **Wache:** je ein Test für die drei Fälle; ein erfolgreicher Rückzug lässt
      keine wirksame öffentliche Lesbarkeit zurück.

- [ ] **4 · F04** Ein `revoke()` glaubt seinem eigenen Rücklesen. Das Ergebnis
      von `_write()` wird gegen die Absicht verglichen wie in `grant()`; bei
      Abweichung `SilentDropError`. Zu vergleichen sind drei Dinge, nicht eins:
      das entzogene Recht, die zu behaltenden Einträge und der Vererbungszustand
      — ein Server, der die halbe ACL übernimmt, ist der interessantere Fall.
      **Wache:** vollständig ignorierte und teilweise übernommene Änderung.

## B · Vollständigkeit über die Schichten

- [ ] **5 · F08** `search_in_collection()` meldet auch die materialseitige
      Kürzung. Je Sammlung sagt `total_materials > returned_materials`, dass
      nicht alles bewertet wurde; das gehört in `truncated`. Weil `truncated`
      damit vier Ursachen bekommt, kommt der **Grund** dazu — der Bericht
      empfiehlt es, und ohne ihn ist die Zahl für den Aufrufer nicht handhabbar.
      **Wache:** der Fall des Berichts (zwei Materialien, Treffer an zweiter
      Stelle, `limit=1`) findet den Treffer oder meldet `truncated=True` —
      **und derselbe Fall ohne vom Server genannte Gesamtzahl**.

- [ ] **6 · §5.2** `collection_stats()` zählt nicht die gekürzte Kinderliste.
      `collections` stammt aus `len(page["collections"])`, obwohl daneben
      `total_collections` und `collections_truncated` liegen. Gemessen: sieben
      Untersammlungen, `sample=3`, gemeldet werden drei.
      **Wache:** die gemeldete Zahl ist die genannte Gesamtzahl, und die
      Unvollständigkeit steht daneben.

- [ ] **7 · F09** Eine unvollständig gelesene Variantenliste erzeugt keine
      scheinbar gesicherte Ersatzvariante. Heute wird bei mehr als 50 Varianten
      `rendered_id` geleert und auf die erste geladene zurückgefallen — „nicht
      konfiguriert" und „nicht geladen" sehen gleich aus. Die beiden Zustände
      werden getrennt; eine gekürzte Liste sagt es, statt zu raten.
      **Wache:** 51 Varianten, `default="v50"`; und `choose()` weist eine
      existierende, nur nicht geladene Variante nicht mehr als unbekannt ab.

## C · Robustheit

- [ ] **8 · F05** Die Kodierung wird genau einmal verarbeitet. Wird aus
      entpacktem Inhalt eine neue Antwort gebaut, dürfen `Content-Encoding` und
      `Content-Length` nicht die der komprimierten sein.
      **Wache:** derselbe Text als unkomprimiert und als gzip, je mit und ohne
      Grenze — vier Fälle, ein Ergebnis. **Und die Gegenprobe bleibt stehen:**
      ein entpackt zu großer Inhalt wird weiterhin abgelehnt.

- [ ] **9 · F07** `path_segment()` weist `.` und `..` zurück. `quote(safe="")`
      kodiert alles, was Pfadgrenzen verschieben *kann* — außer den beiden
      Werten, die selbst welche sind. Gemessen verliert `.` ein Segment und
      `..` zwei. Der generierte Client hat dieselbe Stelle; **von Hand wird dort
      nichts geändert**, das gehört zu Schritt 14.
      **Wache:** beide Werte vor jedem Netzaufruf abgelehnt; zulässige
      Sonderzeichen weiterhin korrekt kodiert.

- [ ] **10 · F11** `TextExtraction` schließt nur, was sie selbst erzeugt hat.
      `Transport` merkt sich das Eigentum seit jeher (`_owns_client`) —
      gegengemessen, dort bleibt ein eingebrachter Client offen. Dieselbe Zeile,
      dasselbe Muster.
      **Wache:** eingebrachter Client übersteht `aclose()` und den
      Kontextmanager; selbst erzeugter wird weiterhin geschlossen.

- [ ] **11 · F14** Ganzzahlige Steuerparameter werden als solche geprüft.
      `at_least()` prüft Zahl, Endlichkeit und Untergrenze — für Sekunden
      richtig, für eine Semaphore nicht: `asyncio.Semaphore(1.5)` erreicht die
      Null nie, an der sie blockieren würde. Gemessen: zehn gleichzeitige
      Anfragen bei `max_concurrency=1.5`, zwei bei `max_concurrency=2`. Eine
      eigene Prüfung für `max_concurrency`, `max_retries` und
      `retries_before_switching`, in allen drei Clients.
      **Wache:** `1.5`, `"2"` und `inf` werden abgelehnt; eine gültige Grenze
      hält bei parallelen Anfragen.

- [ ] **12 · F06** Die Fehlermeldung von `check_url()` maskiert das eingebettete
      Passwort. `mask_userinfo()` gibt es seit SEC-1 und steht zwei Module
      weiter; `refuse_userinfo()` benutzt es bereits. Eine Zeile.
      **Wache:** weder die Ausnahme noch ein daraus gebautes Agentenergebnis
      gibt den Dummy-Wert wieder.

## D · Parser und Fehlerverträge

- [ ] **13 · F12** Markdown-Grenzen und Überschriften nach den Regeln, die ein
      Renderer anwendet. Zwei getrennte Ursachen: `_FENCE` behält die
      Öffnungslänge nicht (ein Dreifach-Fence schließt einen Vierfach-Block, und
      der Rest des Beispiels zerfällt in Stücke — gemessen an
      `_fenced_spans`), und `.rstrip("#")` nimmt Überschriften wie `C#` die
      Raute. Ein fremder Markdown-Parser wäre eine neue Abhängigkeit für zwei
      Regeln; die Öffnungslänge mitzuführen ist kleiner.
      **Wache:** drei bis fünf Backticks und Tilden, verschachtelte
      Beispiel-Fences, ungeschlossene Blöcke; `C#`, `F#`, gesetzte
      Abschlussmarkierungen.

- [ ] **14 · F13** Eine Fehlerantwort, die kein JSON-Objekt ist, bleibt im
      Vertrag. `response.json()` gelingt auch für `['slow down']`, und `.get()`
      darauf ist ein `AttributeError` statt eines `RateLimitedError` — gemessen
      über `_error()` und über `chat()`. Erst die Form prüfen, sonst der
      Textrückfall; Status und `Retry-After` hängen ohnehin nicht am Format.
      **Wache:** Objekt, Liste, String, `null`, kaputtes JSON, HTML — sechs
      Formen, je die passende Ausnahme. Die Objektform bleibt gebunden.

- [ ] **15 · F10** *(nur nach Entscheidung, siehe unten)* Die
      URL-Normalisierung wird komponentenweise. Schema und Host bleiben
      groß-/kleinschreibungsblind, Pfad und Query behalten ihre Bedeutung.
      Betroffen: der Modul-Docstring, die Testdatei und
      `test_nur_die_gleiche_adresse_zaehlt`, dessen Beispiel `URL.upper()` dann
      keine Dublette mehr ist.

## E · Generierte Schicht und dauerhafte Absicherung

- [ ] **16 · F15** Die beiden dokumentierten Erfolgsantworten werden übernommen.
      Nicht von Hand in generierten Dateien: die Spezifikation wird im
      Erzeugungsweg normalisiert, wie `strip_path_param_defaults()` es schon
      tut — `application/text` ist kein gültiger MIME-Typ und meint `text/plain`,
      `*/*` an einer Inhaltsroute meint Bytes. Dazu die Berichtigung in
      `ARCHITECTURE.md`/`.de.md`: nicht eine Warnung, sondern sieben Antworten,
      davon zwei Erfolge.
      **Wache:** beide Antworten im normalen *und* im strengen Modus; und eine
      Wache, die die Zahl der nicht übernommenen Antworten an der Spec
      auszählt — so altert der Satz in der Doku nicht ein zweites Mal.

- [ ] **17 · §5.4** Zwei Gates in die CI, die diese Runde gebraucht hätte:
      Bau plus Installation aus dem Wheel, und eine Neugenerierung mit sauberem
      Diff. Beides lief in der Prüfung erfolgreich — als Gate hätte es F15
      früher gezeigt.

- [ ] **18 · §5.3** Der unterstützte Kontext für `--output` steht in
      ARCHITECTURE, nicht nur als Kommentar im Skript. Gemessen (und im Skript
      bereits notiert): außerhalb des Projektlayouts erzeugt derselbe Generator
      aus derselben Spec 556 andere Dateien.

## Zu entscheiden, bevor es losgeht

1. **F10 — eine dokumentierte Zusage ändern?** Der Bericht hat technisch recht,
   die heutige Form ist gemessen vom MCP übernommen und durch einen Test
   festgehalten. Empfehlung: **ändern**, komponentenweise. Ein falsches „gibt es
   schon" mit `if_exists="return"` gibt den falschen Datensatz zurück, und das
   ist der teurere Fehler. Aber es ist eine Vertragsänderung und gehört in die
   Release-Notiz.

2. **F02 — ablehnen oder filtern?** Empfehlung: **ablehnen**. Ein Filter müsste
   fremde Header-Namen aufzählen und wäre eine Zusage, die er nicht halten kann.
   Kostet: ein eingebrachter Client mit eigenen Zugangs-Headern (etwa hinter
   einem Gateway) wird unbrauchbar. Wer ihn braucht, richtet die Zugangsdaten
   über `credential=` ein.

3. **§5.1 und §6 sind nicht Teil dieses Plans.** Konkurrierende Änderungen
   (`ChangePlan` ohne Vorprüfung) und die zehn Funktionsvorschläge sind Bau,
   nicht Reparatur. Der Bericht empfiehlt selbst, sie auf die verlässlichen
   Verträge zu setzen — also nach A bis E, als eigene Entscheidung.

## Was nicht geprüft wurde

Der Bericht hat ausdrücklich keine Live-Aufrufe gemacht; meine Nachstellungen
auch nicht. Die Rechtefälle aus A gehören nach dem Fix **auf Staging gemessen**
— Sitzungsvorrang, Vererbung, still verworfene Änderungen — im eigenen
Wegwerf-Ordner wie die übrigen Schreibtests. Vorher ist die ACL-Korrektur an
einem Modell belegt, nicht an einem Server.
