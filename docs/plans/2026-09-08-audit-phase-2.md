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
- [ ] **8 · ARC-1** `fields`, `ranking`, `language` aus `flows/` heraus,
  `cap_text` aus `agent/` heraus; dazu ein Test über die Import-Richtung.
- [ ] **9 · COR-5 + COR-3** Die Schreibabläufe behalten die angelegte id, wenn
  ein späterer Schritt scheitert; Rücklesen prüft gegen einen Stand von **vor**
  dem Schreiben, nicht gegen Textgleichheit.
- [ ] **10 · TST-1 / MNT-2 + COR-4** Der Spiegel wird auf Verhalten geprüft und
  bekommt echte Rückgabetypen; der Schleifen-Thread wird auch bei gescheiterter
  Konstruktion geschlossen.
- [ ] **11 · DEP-2 / DEP-1 / OPS-1** Regenerierung gepinnt und mit Herkunft
  vermerkt, Phantom-Abhängigkeiten weg, CI mit `--locked`.
