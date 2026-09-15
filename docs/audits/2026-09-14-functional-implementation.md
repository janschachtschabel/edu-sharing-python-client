# Funktionaler Audit: Umsetzung für Git-Version 0.3.0

Ausgangsstand: `7d85186ffd63690281dd6d8e819092fd2d41d4fc` (`main`).
Umsetzung nach Better Coding Workflow 2.12.0 mit Entwurf, Regressionstests,
unabhängigem Review und Prüfung des installierbaren Pakets.

## Befunde und Ergebnis

| Befund / Anforderung | Umsetzung | Nachweis |
|---|---|---|
| F01: feste Anwendungsfelder beim Schreiben | `MetadataProfile` trennt Lese-Fallbacks, Schreibziele und Such-Aliase. Ein explizites neutrales/eigenes Profil erbt keine WLO-Felder. | `tests/test_metadata_profile.py` |
| F02: Rückgaben verändern den Vokabular-Cache | Unabhängige Listen, unveränderliche Werteinträge | `tests/test_vocab.py` |
| F03: URNs/Codes werden nicht als bekannte Identitäten erkannt | Exakter gespeicherter Schlüssel vor Label-Auflösung; explizite `raw_filters` für andere Rohwerte | `tests/test_vocab.py`, `tests/test_generic_search.py` |
| F04: `related` verliert Identität über den Umweg eines Labels | Gespeicherte Werte direkt verwenden; `based_on_values` ausgeben | `tests/test_generic_search.py` |
| F05: Ranking liest feste Schlagwortfelder | Schlagwörter aus dem Profil; DTOs bleiben kopierbar und JSON-serialisierbar | `tests/test_metadata_profile.py` |
| MDS über API laden und im Speicher halten | `repo.metadata.load/fields`, TTL, Locale, Refresh/Invalidierung, unabhängige Rückgaben | `tests/test_metadata_catalog.py` |
| Vokabulare wiederverwenden | Begrenztes paralleles Vorladen, umgekehrte Label-Auflösung, JSON-Snapshot/Restore mit Kontext- und Altersprüfung | `tests/test_metadata_catalog.py` |
| URI/Label-Flows | `value_fields` und `entries`; Locale und strenge Filterprüfung auch bei Reranking und gemischter Suche | `tests/test_generic_search.py` |
| Wiederverwendbare Anwendungsketten | `prepare_material`, `place_material`, `collection_context` und `collections.add_reference` | `tests/test_composed_flows.py` |
| Synchrone Aufrufe und Beispiele | Neue Adapter, erweiterte Aufrufwachen und zwei ausführbare Beispiele | `tests/test_sync_surface.py`, `tests/test_generic_examples.py` |

Reranking war bereits optional integriert. Es bleibt lokal und benötigt kein
LLM; Suchoptionen und profilabhängige Schlagwörter sind jetzt durchgereicht.
Der funktionale Vergleich mit MCP/Chatbot/Ideendatenbank dient als Orientierung,
nicht als Übernahme ihrer festen WLO-Anwendungsfelder in den generischen Kern.

## Im Review zusätzlich behoben

- Eigene Titel gelten auch in der Suche unter einer Sammlung. Die Prüfung
  geschriebener Sammlungs-REST-Titel bleibt beim tatsächlichen REST-Vertrag.
- `dataclasses.asdict`, `replace` und `deepcopy` funktionieren für profilierte
  Suchtreffer. Der DTO enthält keine nicht serialisierbare Mapping-Proxy-Konfiguration.
- Lokale Filterfehler werden vor parallelen Suchzweigen geprüft;
  `strict=True` bleibt auch mit Reranking ein `ValidationError`.
- Die MDS-Pflichtfeldprüfung verwendet `id` und `isRequired` aus dem API-Vertrag.
- Bereits öffentliche Materialien lassen sich erfolgreich platzieren und
  verschieben; der Änderungs-Bool von `publish()` ist kein Öffentlichkeitsstatus.
- Vorbereitete Entwürfe behalten die URL als Argument, damit `if_exists="raise"`
  beim späteren Speichern erneut geprüft wird.
- Unvollständige URL-Suchen, ignorierte Kriterien, fehlende URL-Leserollen oder
  fehlende URL-Projektionen ergeben Unsicherheit statt behaupteter Abwesenheit.
- Der Sammlungskontext kann eigene Skill-Konventionen und Kontextfilter nutzen.

Unabhängiges Abschlussreview: Spec compliance, Security, Correctness,
Performance, Maintainability, Testing und Docs jeweils PASS; keine verbleibenden
belastbaren Findings im geprüften Diff. Fehler wurden vor dem Fix mit
HTTP-Mocks reproduziert und danach erneut geprüft.

## Prüfungen

- Vollständige Offline-Suite: **2.662 bestanden, 13 übersprungen, 196 abgewählt**
  (90,30 Sekunden, Python 3.12). Ruff ohne Befunde, mypy ohne Fehler in 76 Quelldateien.
- `uv sync --group dev --locked --offline` und `uv lock --check --offline`.
- Wheel und Source-Distribution über `uv build --offline`; Installation in
  separater Umgebung, alle 1.206 Module importiert, profilierter DTO serialisiert.
- `pip-audit --skip-editable`: keine bekannten Schwachstellen in Abhängigkeiten.
- Skill-Validierung, Synchronisation von Referenzen/Beispielen und reproduzierbarer
  ZIP-Bau; Dokumentationswachen prüfen Namen, Optionen, Signaturen und Verzeichnisse.

Im lokalen Offline-Testprozess wurden die von der Arbeitsumgebung gesetzten
Proxy-Variablen entfernt: ihr SOCKS-Proxy benötigt einen optionalen Treiber,
der nicht zu den Bibliotheksabhängigkeiten gehört. Das Lockfile blieb dabei
unverändert. Mypy wurde mit einem eigenen frischen Cache geprüft.

## Verbleibende Grenzen

`metadata_profile=None` erhält das benannte WLO-Kompatibilitätsprofil. Wer keine
WLO-Anwendungsfelder übernehmen will, übergibt ausdrücklich `MetadataProfile()`
oder ein eigenes Profil. Technische edu-sharing-Verträge wie `cm:name`,
Sammlungs-REST-Felder und Referenz-/Seitenprotokolle bleiben bestehen.
Skill-Inhaltsarten werden separat über `SkillConventions` konfiguriert.

Ein MDS-Widget beweist keine Suchbarkeit. Die Entwurfsprüfung umfasst deklarierte
Pflichtfelder, keine vollständige Prüfung von Bedingungen, Datentypen, Rechten
oder serverseitigen Regeln. URL-Dublettenprüfungen bleiben von Sichtbarkeit und
Indexverzögerung abhängig. Mehrstufige Schreibflows sind keine Transaktionen.
Snapshots dürfen nur im passenden Sichtbarkeitskontext wiederverwendet werden.

Zusätzliche Live-Abnahme auf unterschiedlichen Installationen wurde nicht
durchgeführt. 0.3.0 ist deshalb vorerst eine Git-Version; der Release-Tag bleibt
bis zur vorgeschriebenen Live-Abnahme offen. Keine PyPI-Veröffentlichung.
