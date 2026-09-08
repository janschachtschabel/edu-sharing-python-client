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
- [ ] **13 · PRF-2, PRF-3, PRF-4, PRF-5** Die Deckel und die Bündel.
  - PRF-2: `describe_many` ist das einzige unbegrenzte Fan-out.
  - PRF-3: serielle `await`s, wo die Aufrufe unabhängig sind. Enthält zwei
    Punkte, die der Bericht selbst als *needs verification* führt.
  - PRF-4: der Vokabular-Cache läuft nie ab, obwohl ARCHITECTURE eine TTL
    behauptet.
  - PRF-5: `add_material` fragt bei jedem Aufruf ohne `parent_id` erneut
    `whoami()`.
- [ ] **14 · TST-3, TST-6, OPS-2, OPS-3** Aufräumen, Pins, CI und die
  geschriebenen Abläufe.
- [ ] **15 · DOC-3 bis DOC-7** Der Architektur-Nachweis, die Zahlen, die
  Beispiele und die Docstrings — die Zahlen möglichst abgeleitet, damit die
  Wächter sie besitzen statt der Prosa.

Danach: Phase 4 (Politur) der Roadmap.
