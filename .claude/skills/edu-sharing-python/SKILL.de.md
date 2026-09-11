<!--
Begleitdatei, kein eigener Skill: absichtlich ohne Frontmatter. Frontmatter ist
das, was eine Datei zu einem Skill macht -- zwei Skills mit fast denselben
Ausloesern wuerden einander in die Quere kommen, und die englische Fassung
traegt die deutschen Ausloeser bereits in ihrer description. Wer daraus doch
einen eigenen Skill machen will, legt ein eigenes Verzeichnis an und setzt
dort Frontmatter.

Beide Fassungen stehen unter denselben Tests: tests/test_docs_complete.py.
-->

# edu-sharing für Python — wie man sie benutzt

*[English version: SKILL.md](SKILL.md)*

Die Bibliothek unter `github.com/janschachtschabel/edu-sharing-python-client` (Paket
`edu-sharing-python-client`, Import `edusharing`). Sie umhüllt die REST-API von
edu-sharing und drei Dienste daneben, und ihr zentrales Versprechen lautet:
**ein Schreibvorgang, der nicht stattgefunden hat, wird als Fehlschlag gemeldet,
nicht als Erfolg.**

**Dieser Skill behandelt die Bibliothek.** Für die rohe REST-API, das
WLO-Datenmodell (Quelldatensatz, Spider, replicationsource), Lizenzschlüssel
oder NGSearch-Rumpffelder ist `wlo-edu-sharing-api` zuständig. Für
Instanzadressen und Variablennamen `wlo-environments`. Die sind die Wahrheit
über den *Betrieb*, dieser hier über die *Python-Oberfläche*.

**Zwei Fassungen, eine Quelle.** Die Bezeichner, um die es geht, sind englisch,
und `SKILL.md` ist die Fassung, die ein Modell lädt — sie trägt die deutschen
Auslöser schon in ihrer Beschreibung, eine deutsche Anfrage aktiviert sie also
ohnehin. Diese hier ist dieselbe Wegweisertabelle für Menschen, die lieber
deutsch lesen. Beide stehen unter denselben Tests: `tests/test_docs_complete.py`
lässt keine der beiden einen Ablauf auslassen, einen Aufruf erfinden, eine
Umgebungsvariable nennen, die der Code nicht liest, oder ins Leere verweisen.

---

## 1. Orientierung in sechzig Sekunden

```bash
uv pip install -e .        # noch nicht auf PyPI
```

```python
from edusharing import Repository

with Repository("https://repository.staging.openeduhub.net") as repo:
    result = repo.search("Bruchrechnung", limit=5)
    for hit in result.hits:
        print(hit.title, hit.url)
```

Zwei Ebenen, beide bleiben:

| | API-Ebene | Ablauf-Ebene |
|---|---|---|
| Erreichbar als | `repo.search(...)`, `repo.node(...)` | `repo.flows.search(...)` |
| Liefert | Objekte — `SearchResult`, `Node` | schlichtes `dict`, fertig für `json.dumps` |
| Gut für | Python gegen edu-sharing schreiben | die Antwort weiterreichen |
| Anfragen | ein Endpunkt je Aufruf | ein Aufruf, mehrere Endpunkte |

**Faustregel:** geht das Ergebnis an ein Modell, ein MCP-Werkzeug oder eine
HTTP-Antwort, dann `repo.flows`. Schreiben Sie den aufrufenden Code selbst,
dann die API-Ebene.

`Repository` ist blockierend, `AsyncRepository` dieselbe Oberfläche mit `await`.
Innerhalb einer Ereignisschleife die asynchrone, sonst die blockierende.

---

## 2. Die Instanz ist immer ein Parameter

**Nie eine Adresse fest verdrahten.** Die Bibliothek hat keine voreingestellte
Instanz; jeder Einstiegspunkt nimmt eine entgegen, und kein Aufruf darunter
nimmt eine eigene.

```python
repo = Repository(os.environ["EDU_SHARING_URL"], auth=(user, password))
repo = Repository.from_env()      # EDU_SHARING_URL / _USER / _PASSWORD
# benutzer:passwort@ in der URL wird abgewiesen -- auth= oder die Umgebung tragen sie
```

Die drei Nachbardienste bekommen jeder **seine eigene** Adresse und haben
ebenfalls keine Voreinstellung — `from_env()` verweigert ohne die Variable,
statt Daten an einen Host zu schicken, den niemand gewählt hat:

| Dienst | Klasse | Variable |
|---|---|---|
| LLM-Gateway (b-api) | `BildungsAPI` | `B_API_BASE_URL` + `B_API_KEY` |
| dasselbe Gateway, Template-Modus | `BapiTemplates` | `B_API_BASE_URL` + `B_API_KEY` + `EDU_SHARING_METADATASET` |
| Textextraktion | `TextExtraction` | `EDU_SHARING_TEXT_EXTRACTION_URL` |
| Metadata Agent | `MetadataAgent` | `METADATA_AGENT_URL` |

Welche konkreten Adressen zu Staging und Produktiv gehören, steht **nicht** in
diesem Skill und nicht in der Bibliothek — siehe `wlo-environments`.

---

## 3. Welcher Aufruf beantwortet welche Frage

Die vollständige Liste mit Ein- und Ausgabeformen ist
[`docs/REFERENCE.de.md`](../../../docs/REFERENCE.de.md) /
[`docs/REFERENCE.md`](../../../docs/REFERENCE.md). Dies ist die Wegweisertabelle.

*(Die Dateiverweise hier gelten relativ zum Checkout der Bibliothek. Nach
`~/.claude/skills/` kopiert benennen sie Pfade in jenem Repositorium, nicht auf
der Platte.)*

### Finden

| Die Aufgabe | Der Aufruf |
|---|---|
| Material suchen | `repo.flows.search(text, subject=…, limit=…, exclude_ids=…, properties=…)` |
| Material *und* Sammlungen auf einmal | `repo.flows.search_all(text)` |
| nur Sammlungen finden — nach Fach, oder unterhalb einer Sammlung | `repo.flows.find_collections(text, subject=…, parent_id=…)` → `unjudged` lesen |
| welche **Skills** zu einer Aufgabe passen oder in einer Sammlung liegen | `repo.flows.find_skills(text, subject=…, collection_id=…)` — braucht den Metadatensatz, der die Inhaltsart kennt |
| der beste Skill, geladen, mit den Übrigen | `repo.flows.pick_skill(text)` → `reason` lesen |
| mehr wie dieser Knoten | `repo.flows.related(node_id, on=["subject", "level"])` |
| welche Werte lässt ein Feld zu | `repo.flows.vocabulary("subject")` |
| alle Werte eines Feldes, oder eine Teilzeichenkette | `repo.vocab.values(prop)` / `repo.vocab.suggest(prop, "ysik")` — `values` gilt `DEFAULT_CACHE_SECONDS` (1 h) |
| bei unbekannten Filterlabels zurückfragen | höchstens `SUGGEST_LOOKUP_MAX` (10) bekommen Vorschläge; der Rest wird ohne sie gemeldet |
| der Filterwert zu einem Label — **alle** davon | `repo.vocab.resolve_all(prop, "Biologie")` |
| eine schlecht formulierte Anfrage („irgendwas mit Brüchen") | `repo.flows.search(text, rerank=True)` |
| *innerhalb* einer Sammlung suchen | `repo.flows.search_in_collection(collection_id, query)` |
| Sammlungen mit kuratierter Seite finden | `repo.flows.find_pages(text)` |

### Eines lesen

| Die Aufgabe | Der Aufruf |
|---|---|
| alles über einen Knoten, als JSON | `repo.flows.describe(node_id)` |
| mehrere Knoten auf einmal | `repo.flows.describe_many(node_ids)` |
| wo liegt er (Brotkrumenpfad) | `repo.flows.placement(node_id)` |
| was ist in dieser Sammlung | `repo.flows.collection_contents(collection_id)` |
| was hängt *unter* diesem Material | `repo.flows.child_objects(node_id)` |
| was steht *daneben* | `repo.flows.relations(node_id)` |
| was liegt darunter, rekursiv | `repo.flows.browse_tree(collection_id, depth=2)` |
| wie viel ist darin | `repo.flows.collection_stats(collection_id)` |
| die kuratierte Landeseite | `repo.flows.page(collection_id)` |
| der Text eines Materials, wo immer er liegt — und *warum* keiner da ist | `repo.flows.text(node_id, extraction=…)` → `source`, `reason` lesen |
| die Anleitung eines Skills, seine Verweise und Begleitdateien | `repo.flows.skill(node_id)` → `files_reason` lesen |
| welche Skills eine Sammlung freigegeben hat, nach Arbeitszusammenhang | `repo.flows.skill_registry(collection_id, context=…)` → `reason`, `context_match` lesen |
| die Datei selbst | `node.content.download()` / `node.content.text()` |
| die kuratierte Seite als Objekte | `node.page.get()` / `node.page.render(variant)` |
| eine Seite der Kinder eines Knotens | `repo.nodes.children(node_id, limit=…)` |
| wer bin ich, was bietet diese Instanz | `repo.whoami()` / `repo.about()` / `repo.metadatasets()` |
| Text einer Seite, die das Repositorium *nicht* hat | `TextExtraction.text_of(url)` |

### Ändern

| Die Aufgabe | Der Aufruf |
|---|---|
| Material mit Vokabular anlegen | `repo.flows.add_material(title, url=…, subject=…)` · `if_exists=\"return\"` nennt einen vorhandenen Datensatz zu `url`, statt einen zweiten anzulegen (`created`, `existing`) |
| Material ändern | `repo.flows.update_material(node_id, title=…)` |
| Sammlung bauen und füllen | `repo.flows.build_collection(title, node_ids=[…])` |
| vorhandenes Material in eine Sammlung legen | `repo.add_to_collection(collection_id, node_id)` |
| der Sammlungs-Zugriff hinter diesen Abkürzungen | `repo.collections.find/create/update/add/remove` |
| wieder herausnehmen (Material bleibt) | `repo.remove_from_collection(collection_id, node_id)` |
| löschen | `repo.flows.delete(node_id)` |
| Datei hochladen | `node.content.upload(data, filename=…, mimetype=…)` |
| Lösungsblatt anhängen | `node.children.add(data, filename=…, mimetype=…)` |
| zwei Materialien verknüpfen | `repo.relations.create(a, "isPartOf", b)` |
| öffentlich lesbar machen | `node.permissions.publish()` |
| Schlagwörter | `node.add_keywords([...])` / `node.remove_keywords([...])` |

### Redaktionelle Flächen (API-Ebene, außer dem Annehmen eines Vorschlags)

| Die Aufgabe | Der Aufruf |
|---|---|
| kommentieren | `node.comments.add(text)` / `.list()` / `.edit()` / `.delete()` |
| bewerten | `node.rate(4)` / `node.unrate()` |
| einen Wert **vorschlagen** statt ihn zu schreiben | `node.suggestions.propose(prop, value, reason)` |
| einen Vorschlag annehmen oder ablehnen | `node.suggestions.decide(ids, accept=True)` |
| einen Vorschlag **wirksam** annehmen — schreiben, zurücklesen, dann markieren | `repo.flows.accept_suggestion(node_id, suggestion_id)` → `applied` lesen |
| zur Prüfung weiterreichen | `node.workflow.submit("GROUP_redaktion", "TO_BE_CHECKED")` |
| Rechte geben oder nehmen | `node.permissions.grant(who, "Read")` / `.revoke(...)` |
| Gruppen und Mitglieder | `repo.people.memberships()` / `.group(name)` / `.members(name, limit=…)` / `.create_group(name)` / `.add_member(gruppe, wer)` |

### Die Nachbardienste

| Die Aufgabe | Der Aufruf |
|---|---|
| ein Modell fragen | `BildungsAPI.chat(prompt)` |
| über die responses-Route fragen | `.respond(prompt, model=…)` → `.truncated` prüfen |
| das am wenigsten ausgelastete von mehreren | `.chat(prompt, model=["a", "b", "c"])` |
| wie die Modelle gerade dastehen | `.load()` → `.summary()` |
| welche Modelle gibt es | `.models()` |
| billiger denken (Vorgabe) | nichts — `reasoning_effort` steht schon auf `low` |
| mehr denken | `.chat(prompt, reasoning_effort="high")` |
| Einbettungen *(nur OpenAI)* | `.embeddings(texts)` |
| Moderation *(nur OpenAI)* | `.moderate(texts)` |
| Bildgenerierung *(nur OpenAI)* | `.images(prompt)` |
| jede andere durchgereichte OpenAI-Route | `.call("batches", body)` |
| ein Prompt, der auf dem Server liegt, gefüllt aus einem Knoten | `BapiTemplates.chat(configs, context_node_id=…)` |
| … mit Eingaben, denen Sie nicht trauen | `.chat_limited(configs, context_node_id=…, choices=…)` |
| das Modell Metadaten vorschlagen lassen, gespeichert als Vorschläge | `.suggest(configs, widgets, context_node_id=…)` → übernehmen mit `repo.flows.accept_suggestion` |
| Frage-Antwort-Paare zu einem Knoten *(experimentell, gespeichert)* | `.qas(node_ids)` — braucht Write für das eigene Konto des Gateways |
| Text hinter einer URL | `TextExtraction.text_of(url, method="simple")` |
| was in den JSON-Bereich einer Inhaltsart gehört | `MetadataAgent.content_types()` / `.schema(file)` |

### Bausteine für KI-Anwendungen

| Die Aufgabe | Der Aufruf |
|---|---|
| eine Form für Erfolg und Fehlschlag | `as_result(awaitable, format=format_results)` → `ToolResult`: `.ok` `.text` `.data` `.error` `.error_type` `.metadata` |
| ein Treffer als knapper Text | `format_hit(hit)` / `format_results(result)` |
| fremden Text als Daten markieren | `as_untrusted(text, label="description")` |
| Steuerzeichen entfernen | `sanitize_text(text)` / `one_line(text)` |
| eine interne Adresse ablehnen | `check_url(url)` / `is_safe_url(url)` |
| eine Änderung planen, ein Mensch bestätigt | `plan_update(node, title=…)` → `ChangePlan`: `.node` `.changes` `.unchanged` `.has_changes` `.can_write` `.describe()` `.apply()` |

### Die ganze Fläche, Objekt für Objekt

Die Tabellen oben weisen den Weg für die häufigen Aufgaben. Alles
Übrige erreicht man über ein Objekt, das man ohnehin schon in der Hand hält.
Hier steht jedes öffentliche Glied beim Namen, damit nichts geraten werden
muss — die Argument- und Rückgabeformen stehen in `docs/REFERENCE.de.md`.

**Hinein**

| Man hält | Woher | Was darauf ist |
|---|---|---|
| `Repository` | `Repository(url, auth=…)` oder `.from_env()` | `.search()` `.node()` `.create_node()` `.children()` `.create_collection()` `.update_collection()` `.add_to_collection()` `.remove_from_collection()` `.find_collections()` `.resolve()` `.resolve_all()` `.about()` `.whoami()` `.metadatasets()` `.close()`; `.url` `.credential` `.metadataset` `.raw` `.flows` `.people` `.relations` `.nodes` `.collections` `.vocab` `.searcher` |
| `AsyncRepository` | dasselbe, innerhalb einer Ereignisschleife | dieselben Namen mit `await`, `.aclose()` statt `.close()` |
| `Credential` | `BasicCredential(user, pw)`, `BasicCredential.from_env()`, `AnonymousCredential()`, `credential_from(…)` | `.headers()` `.is_anonymous` `.username` |

**Ein Knoten und alles, was daran hängt**

| Man hält | Woher | Was darauf ist |
|---|---|---|
| `Node` | `repo.node(node_id)`, `repo.create_node(…)` | lesen `.id` `.name` `.title` `.type` `.aspects` `.original_id` `.is_reference` `.redirected_from` `.url` `.access` `.can_write` `.is_public` `.preview_url` `.properties` `.keywords` `.raw` `.get()` `.get_all()` `.labels()` `.parents()` `.collections()`; schreiben `.update()` `.set_property()` `.add_keywords()` `.remove_keywords()` `.rate()` `.unrate()` `.delete()`; Türen `.content` `.children` `.permissions` `.workflow` `.comments` `.suggestions` `.page` `.rating` |
| `NodeContent` | `node.content` | `.download()` `.text()` `.upload()` `.set_preview()` `.delete_preview()`; `.has_content` `.mimetype` `.size` `.download_url` |
| `NodePermissions` | `node.permissions` | `.get()` `.grant()` `.revoke()` `.publish()` `.unpublish()` |
| `Permissions` | `node.permissions.get()` | `.own` `.inherited` `.effective` `.inherits` `.is_public` `.allows()` `.find()` |
| `Ace` | `permissions.find(…)` | `.authority` `.authority_type` `.permissions` `.allows()` `.for_authority()` `.as_body()` |
| `Workflow` | `node.workflow` | `.history()` `.submit()`; `WorkflowStep`: `.status` `.receivers` `.comment` `.editor` `.at` |
| `Comments` | `node.comments` | `.list()` `.add()` `.edit()` `.delete()`; `Comment`: `.id` `.text` `.author` `.created` `.reply_to` |
| `Suggestions` | `node.suggestions` | `.list()` `.propose()` `.decide()`; `Suggestion`: `.id` `.property` `.value` `.status` `.why` `.confidence` `.author` |
| `ChildObjects` | `node.children` | `.list()` `.add()` |
| `Rating` | `node.rating` | `.average` `.count` `.own` |
| `NodePage` | `node.page` | `.get()` `.render()` |

**Sammlungen, Personen, Beziehungen, Vokabular**

| Man hält | Woher | Was darauf ist |
|---|---|---|
| `Collections` | `repo.collections` — seit dem 10.09.2026 auch auf `Repository` blockierend | `.find()` `.create()` `.update()` `.add()` `.remove()` |
| `Nodes` | `repo.nodes` — seit dem 10.09.2026 auch auf `Repository` blockierend | `.get()` `.create()` `.children()` `.repository_url` `.wrap(data)`; `ChildPage`: `.nodes` `.total` `.offset` |
| `Search` | `repo.searcher` — seit dem 10.09.2026 auch auf `Repository` blockierend | `.search()` |
| `Vocabulary` | `repo.vocab` — seit dem 10.09.2026 auch auf `Repository` blockierend | `.values()` `.suggest()` `.resolve()` `.resolve_all()` `.clear_cache()`; `VocabularyValue`: `.uri` `.label` |
| `People` | `repo.people` | `.memberships()` `.group()` `.members()` `.create_group()` `.delete_group()` `.add_member()` `.remove_member()`; `Group`: `.name` `.short_name` `.display_name` `.type` `.signup`; `Member`: `.name` `.is_group` |
| `Skills` | `repo.skills` | `.search()` `.get()` `.registry()` `.pick()`; `SkillConventions`: `.type_property` `.skill_type` `.registry_type` `.registry_mark` `.markdown_mimetypes` `.block_kinds`; `WLO_SKILLS` |
| `SkillSummary` / `SkillDocument` | `.search().hits` / `.get()` | `.id` `.original_id` `.title` `.description` `.keywords` `.url` `.download_url`; das Dokument dazu `.content` `.references` `.files` `.files_reason` `.folder_file_count`; `SkillFile`: `.id` `.title` `.mimetype` `.size` `.download_url`; `SkillSearch`: `.hits` `.unresolved` `.truncated` |
| `SkillRegistry` | `repo.skills.registry(collection_id)` | `.collection_id` `.registry_id` `.registry_title` `.markdown` `.entries` `.unresolved` `.contexts` `.general` `.ambiguous` `.truncated` `.contexts_truncated` `.reason` `.context_match` `.scan_truncated`; `RegistryEntry`: `.node_id` `.title` `.description` `.keywords` `.context` |
| `SkillReference` / `MarkdownSection` / `RegistryContext` / `RegistryGeneral` / `ContextLayout` | `parse_blocks(text)` / `parse_sections(text)` / `layout_contexts(text, blocks)` | `.kind` `.title` `.url` `.node_id` `.offset` / `.level` `.title` `.heading_start` `.body_start` `.end` / `.title` `.level` `.path` `.instruction` `.skills` `.range` / `.instruction` `.skills` / `.contexts` `.general` `.paths` `.truncated` |
| `Relations` | `repo.relations` | `.of()` `.create()` `.delete()` `.approve()`; `Relation`: `.type` `.from_id` `.to_id` `.from_title` `.to_title` `.ai_generated` `.approved` `.created_by` `.created_at` `.opposite_of()`; `RELATION_TYPES` nennt die zulässigen Arten |

**Was eine Suche zurückgibt**

| Man hält | Woher | Was darauf ist |
|---|---|---|
| `SearchResult` | `repo.search(…)` (der Ablauf liefert dasselbe als `dict`) | `.hits` `.total` `.total_is_lower_bound` `.facets` `.suggestions` `.unresolved` `.ignored` `.warnings` `.raw` |
| `SearchHit` | `result.hits[i]` | `.id` `.title` `.url` `.description` `.source_url` `.mimetype` `.mediatype` `.preview_url` `.download_url` `.license` `.size` `.original_id` `.properties()` `.labels()` |
| `Facet` | `result.facets` | `.property` `.values` `.other_count` `.truncated`; `FacetValue`: `.value` `.count` |
| `UnresolvedFilter` | `result.unresolved` | `.field` `.value` `.suggestions` |

**Die Instanz und redaktionelle Seiten**

| Man hält | Woher | Was darauf ist |
|---|---|---|
| `Identity` | `repo.whoami()` | `.authority` `.username` `.display_name` `.is_anonymous` `.home_folder` `.raw` |
| `About` | `repo.about()` | `.repository_version` `.renderservice_version` `.api_version` `.services` `.plugins` `.features` `.themes_url` `.raw` |
| `MetadataSet` | `repo.metadatasets()` | `.id` `.name` |
| `CuratedPage` | `node.page.get()` | `.collection_id` `.folder_id` `.variants` `.rendered_id` `.total_variants` `.truncated` `.document` `.rendered` `.by_position` `.variant()` |
| `PageVariant` | `page.variant(…)`, `variant_from_node(…)` | `.id` `.title` `.is_template` `.target_group` `.educational_contexts` `.intention` `.education_levels` `.swimlanes` `.readable` `.node_ids` |
| `Swimlane` / `SwimlaneItem` | `variant.swimlanes` | `.heading` `.type` `.items` / `.widget` `.node_id` |
| `Ancestry` | `ancestry_of(…)`, `collections_of(…)` | `.node` `.parents` `.scope` |

**Die Nachbardienste als Objekte**

| Man hält | Woher | Was darauf ist |
|---|---|---|
| `BildungsAPI` | `BildungsAPI(key, base_url=url)` oder `.from_env()` | `.chat()` `.respond()` `.models()` `.load()` `.embeddings()` `.moderate()` `.images()` `.call()` `.aclose()` |
| `Answer` | `.chat()` / `.respond()` | `.text` `.status` `.reason` `.model` `.truncated` `.raw` |
| `Model` | `.models()` | `.id` `.name` `.demand` `.status` `.input` `.output` `.owned_by` `.shutdown_date` `.is_ready` `.can_chat` `.is_retired_on()` |
| `LoadReport` | `.load()` | `.provider` `.models` `.reports_load` `.retired` `.total` `.least_loaded` `.summary()`; freie Funktionen `load_report()` `rank_models()` `rank_among()` `pick_model()` `is_rankable()` |
| `Moderation` / `GeneratedImage` | `.moderate()` / `.images()` | `.flagged` `.categories` `.scores` / `.url` `.b64` `.revised_prompt` |
| `BapiTemplates` | `BapiTemplates(key, base_url=url, metadataset=…)` oder `.from_env()` — braucht kein `BildungsAPI` | `.chat()` `.chat_limited()` `.respond()` `.respond_limited()` `.images()` `.images_limited()` `.suggest()` `.qas()` `.aclose()`; `NodeConfig`: `.node_id` `.config_name`; die Typen `Config` und `Values`; `DEFAULT_USER` |
| `TextExtraction` | `TextExtraction(url)` oder `.from_env()` | `.text_of()` `.ping()` `.aclose()`; `ExtractedText`: `.url` `.text` `.lang` `.status` `.char_count` `.truncated` `.reason` `.detail` |
| `MetadataAgent` | `MetadataAgent(url)` oder `.from_env()` | `.schemas()` `.schema()` `.content_types()` `.content_type_for()` `.clear_cache()` `.aclose()`; `SchemaInfo`: `.file` `.profile_id` `.groups` `.field_count`; `ContentType`: `.uri` `.schema_file` `.label` `.icon` |
| `Transport` | `repo.raw` | `.request()` `.json()` `.is_repository_url()` `.aclose()` — für Routen, die diese Bibliothek nicht umhüllt |

**Freie Funktionen, die man kennen sollte**

| Die Aufgabe | Der Aufruf |
|---|---|
| aus einem Titel einen zulässigen `cm:name` machen | `name_from_title(title)` |
| Kurznamen zu Eigenschaften machen, Labels aufgelöst | `resolve_vocabulary(repo, aliases, every_value=…)` → `(properties, unresolved)`; `every_value=True` für einen Lesefilter |
| einen Filter lokal an einem Datensatz beurteilen | `carries(props, prop, values)` |
| einen Sammlungsbaum mitsamt Datensätzen gehen | `walk_collections(repo, collection_id, depth=…, max_collections=…)` → `(entries, opened, truncated)` |
| Seiten unter schon geholten Sammlungstreffern | `pages_among(found, text)` |
| ein Skill-Dokument ohne I/O lesen | `parse_blocks(text)` / `parse_sections(text)` / `layout_contexts(text, blocks)` |
| die Registry einer Sammlung, außerhalb des Zugriffsobjekts | `load_registry(repo, collection_id)` |
| eine schwache Anfrage verbreitern | `expand_query(query)` → `QueryVariant`: `.label` `.weight` `.text` |
| einen Treffer selbst gegen die Anfrage bewerten | `score_hit(hit, query, aliases)` / `query_terms(query)` / `term_matches(…)` |
| Doppelte zusammenfalten | `deduplicate(hits)` |
| ein Ergebnis als schlichtes JSON | `result_as_dict(result)` / `hit_as_dict(hit)` |
| die Stoppwort- und Synonymlisten | `LanguageProfile`: `.stopwords` `.framing` `.synonyms`; `GERMAN_SYNONYMS` |
| eine Instanz-URL normalisieren | `normalize_repository_url(raw)` / `rest_base(repository_url)` / `path_segment(value)` / `is_unroutable_host(host)` |
| beurteilen, ob eine Adresse geholt werden darf | `unsafe_url_reason(url)` — `None` heißt: sie darf; alles andere ist die Absage, fertig zum Protokollieren |
| nur die Schreibweise beurteilen (den Host löst man selbst auf) | `unsafe_url_syntax(url)` — Backslash oder eingebettete Anmeldedaten, die zwei Wege, auf denen Parser auseinandergehen |
| eine Suche, die neu ordnet und beide Hälften meldet | `search_reranked(repo, text)` |
| jede Untersammlung einer Sammlung | `sub_collections(repo, id)` |
| die Bewertung eines Knotens, den man hält | `rating_of(node)` / `rate(…)` / `unrate(…)` |
| Text kürzen, bevor er ein Modell erreicht | `cap_text(text, max_chars)` |

**Fehler** — alle erben von `EduSharingError`; ein einziges
`except EduSharingError` fängt daher alles, was diese Bibliothek wirft:

`TransportError` · `AuthenticationError` · `PermissionDeniedError` ·
`NotFoundError` · `ValidationError` · `ConflictError` · `SilentDropError` ·
`ServerError` · `UnsafeUrlError` · `ContentTooLargeError` (ein Download über
`max_bytes`; die Textpfade halten bei `MAX_TEXT_BYTES`, 8 MiB, vor dem Laden an)

`RateLimitedError` (429 — `retry_after` trägt die vom Dienst genannten
Sekunden; kurze Wartezeiten werden für dich abgewartet, eine lange kommt mit
der Zahl bei dir an).

**Wiederholungen** folgen einer Regel für alle drei Clients:
`RetryPolicy(max_retries=…, backoff_base=…, max_retry_after=…)`, deren
`delay(attempt, retry_after=…)` die Wartezeit liefert — gestreut, damit eine
Fan-out-Welle nicht im Gleichschritt zurückkommt — oder `None`, wenn der Dienst
um mehr gebeten hat, als dieser Client abwartet. `RETRYABLE_STATUS` ist der
Statussatz, den die beiden Nachbardienste erneut versuchen,
`DEFAULT_MAX_RETRY_AFTER` (60 s) ist diese Obergrenze, und
`parse_retry_after(value)` liest den Kopf in beiden Schreibweisen, die
RFC 9110 erlaubt. Eine abgewiesene 3xx nennt nur den Zielhost — eine
vorsignierte Adresse trägt ihre Vollmacht in der Abfrage — und legt die
ganze `Location` als `.location` an die Ausnahme.

`edusharing.dto` ist die eine Lesart eines rohen Knotensatzes —
`first(value)` (der erste Wert einer Eigenschaft, `None` bei leerer Liste),
`title_of(raw)` (`title`, dann `cclom:title`, `cm:title`, `cm:name`) und
`stored_title_of(raw)` (dasselbe ohne den Rückfall auf den Namen — was ein
Schreibvorgang erhält), `node_id_of(raw)`, `bare_id(ref)`, `render_url(repository_url, node_id)` und
`page_total(response, default=…)`. Jedes Objekt dieser Bibliothek entsteht
über sie, damit derselbe Datensatz sich immer gleich liest.

`page_cut(records, response, limit)` ist die eine Lesart der Frage *"ist diese
Seite alles?"*. Gefragt wird nach `limit + 1`, dann beantwortet die Seite sie
selbst; aus der genannten Gesamtzahl allein gelesen hiess sie genau dort
"vollständig", wo das Repositorium nichts sagte — also dort, wo die Frage am
meisten wog.

`at_least(name, value, limit)` ist die Grenzprüfung für die **stetigen**
Einstellungen der Clients und `whole_number(name, value, limit)` die für die
**zählenden** (`max_concurrency`, `max_retries`, `retries_before_switching`) —
dort wird eine Bruchzahl abgelehnt, weil eine Semaphore, die 1.5 herunterzählt,
die Null nie erreicht, an der sie blockieren würde;
`check_client(client, timeout=…)` trägt die drei Regeln für einen mitgebrachten Client —
kein `timeout` daneben, kein `follow_redirects=True`, weil httpx eigene Kopfzeilen über
Ursprungsgrenzen hinweg behält und ein API-Schlüssel damit mitwandert, und keine
eigenen Zugangsdaten (`auth=` oder eine Vorgabe-Kopfzeile über httpx' vier hinaus),
weil die an jede Adresse gehen, auch an eine ausserhalb des Repositoriums, und
keine Cookies im Speicher, weil das Abschalten ihn nicht leert und httpx seinen
Inhalt auf jede Anfrage kopiert;
`redirect_error(…)` und `non_json_error(…)` sind die zwei Antworten, die alle vier
Clients auf einen 3xx und auf einen Körper ohne JSON geben — beide innerhalb von
`EduSharingError`, damit nichts aus der Standardbibliothek dem Vertrag entkommt;
`details_withheld(…)` benennt, was ein Fehler bewusst nicht preisgibt.

**Der Rest von `__all__`** ist Maschinerie, die man nur anfasst, wenn man die
Bibliothek erweitert statt sie zu benutzen: `Flows` (der Typ hinter `repo.flows`),
`__version__`, die Konstruktoren `from_response` / `from_node` / `from_raw_header` /
`error_from_response` (und `error_class_for`, das nur sagt, welcher Typ zu
einem Status gehört), die b-api-Rumpfhelfer `build_body` / `read_answer` /
`reasoning_for_responses` und `field_property`, das einen Kurznamen auf seine
Eigenschaft abbildet. Nichts oben setzt voraus, sie zu rufen.

**Benannte Konstanten — die Vorgaben und die magischen Zeichenketten**

Jede Vorgabe unten ist ein Schlüsselwortargument, das man überschreiben kann;
die Konstante gibt es, damit der Wert einen Namen hat, statt in einer Signatur
zu verschwinden.

| Konstante | Wert | Was sie regelt |
|---|---|---|
| `DEFAULT_EFFORT` / `DEFAULT_VERBOSITY` | `"low"` | Denktiefe und Ausführlichkeit bei Modellen, die das können |
| `DEFAULT_MAX_TOKENS` / `DEFAULT_MAX_OUTPUT_TOKENS` | `1000` | die Grenze einer Chat-Antwort / einer Responses-Antwort |
| `DEFAULT_HIT_CHARS` / `DEFAULT_RESULT_CHARS` | `400` / `4000` | wie viel `format_hit` / `format_results` einem Modell reicht |
| `DEFAULT_MAX_CHARS` | `200000` | wo `flows.text` kürzt, an einer Wortgrenze |
| `SKILL_SEARCH_PAGE` / `SKILL_BUNDLE_MAX` / `SKILL_VISIT_MAX` / `SKILL_DEPTH_MAX` | `50` / `50` / `30` / `2` | Skill-Treffer im Pool · Begleitdateien, bevor ein Ordner als Eingang zählt · Sammlungen je Gang · Ebenen, die der Gang hinabsteigt |
| `REGISTRY_SCAN_MAX` / `REGISTRY_MAX` / `REGISTRY_POOL` / `REGISTRY_CONTEXT_MAX` | `50` / `100` / `10` / `50` | Dateien auf der Suche nach der Registry · Einträge je Antwort · Köpfe auf einmal · Kontexte je Antwort |
| `DUPLICATE_SCAN_LIMIT` | `20` | Treffer, die `find_by_url` vergleicht, bevor `add_material` anlegt; `check_before_create` wendet `if_exists` an, `validate_if_exists` weist ein verschriebenes ab |
| `EXCLUSION_MAX` | `200` | das größte Nachladen nach `exclude_ids` — `limit` selbst wird nie gekappt |
| `DEFAULT_POOL` | `25` | wie viele Treffer `search(rerank=True)` vor dem Neuordnen holt |
| `MAX_VARIANTS` | `5` | wie viele Umformulierungen `expand_query` erzeugt |
| `DEFAULT_MAX_COLLECTIONS` / `DEFAULT_MAX_WIDGETS` / `DESCRIBE_MANY_MAX` | `50` / `24` / `50` | Obergrenzen für `browse_tree`, für eine gerenderte Seite und für die verschiedenen IDs, die ein `describe_many` ansieht (es antwortet mit `truncated`) |
| `RELATED_ON` | `("subject", "level")` | die Felder, auf die `related()` standardmäßig vergleicht |
| `METHODS` | `("simple", "browser")` | die Extraktionsverfahren, die `text_of` annimmt |
| `PROPOSAL_BATCH` | `"edusharing-python"` | unter welchem Stapelnamen Vorschläge abgelegt werden |
| `GERMAN` | ein `LanguageProfile` | die deutschen Stoppwort-, Rahmenwort- und Synonymlisten |

| Konstante | Wert | Warum sie einen Namen hat |
|---|---|---|
| `KEYWORD_PROPERTY` | `cclom:general_keyword` | die gemeinsame Schlagwortliste (siehe [TRAPS.de.md 1.6](reference/TRAPS.de.md#16-manche-listen-sind-gemeinsames-eigentum)) |
| `CHILD_ASPECT` / `ORDER_PROPERTY` / `LIST_MAX` | `ccm:io_childobject` / `ccm:childobject_order` / `200` | was ein Kindobjekt kennzeichnet und ordnet, und wie viele eine Auflistung liest, bevor sie wirft |
| `PAGE_REF` / `PAGE_CONFIG` / `VARIANT_CONFIG` | `ccm:page_config_ref` / `ccm:page_config` / `ccm:page_variant_config` | die drei Eigenschaften, an denen eine redaktionelle Seite hängt |
| `EVERYONE` / `CONSUMER` | `GROUP_EVERYONE` / `Consumer` | die Autorität und das Recht, die einen Knoten öffentlich machen |
| `GUEST_AUTHORITY` | `esguest` | wer man ist, wenn sich niemand angemeldet hat |
| `UNTRUSTED_MARKER` | der Rahmen, in den `as_untrusted` Text setzt | damit ein Modell sieht, wo fremder Text beginnt |

`UNSET` ist der Merkwert hinter der Regel **eine Vorgabe darf fallen, ein
ausdrücklicher Wunsch nicht**: wer nichts übergibt, lässt die Bibliothek einen
Parameter weglassen, den ein Modell nicht unterstützt; wer einen Wert
ausdrücklich setzt, bekommt bei einem nicht unterstützten Parameter einen
Fehler statt stillen Verlusts. `ReasoningParam` ist sein Typ.

---

## 4. Wie edu-sharing Metadaten ablegt

Umgezogen nach [reference/TRAPS.de.md, Teil 1](reference/TRAPS.de.md#1-wie-edu-sharing-metadaten-ablegt):
jeder Wert ist eine Liste, vier Namensräume, `cm:name` ist ein Schlüssel,
Vokabularfelder tragen URIs, der Metadatensatz entscheidet, was es gibt,
gemeinsame Listen, Aspekte, und Eigenschaften, die leer ankommen.

---

## 5. Die Fallen — worauf zu achten ist

Umgezogen nach [reference/TRAPS.de.md, Teil 2](reference/TRAPS.de.md#2-die-fallen--worauf-zu-achten-ist):
sechzehn Fallen, jede gegen eine echte Instanz gemessen — von „HTTP 200 heißt
nicht, dass etwas gespeichert wurde“ bis zum Template-Modus. Die eine, die man
vor jedem Ergebnis kennen muss: `total_is_lower_bound`, `truncated`,
`complete`, `collections_truncated`, `scan_truncated` und `contexts_truncated`
sagen jeweils, dass etwas fehlt (Teil 2.3).

---

## 6. Hinter ein Modell stellen

### Text aus dem Repositorium darf nie als Anweisung wirken

Beschreibungen, Titel und Kommentare schreiben Fremde. Vor dem Modellkontext
umschließen:

```python
from edusharing.agent import as_untrusted, sanitize_text

as_untrusted(hit.description, label="description")
```

### Eingaben, denen Sie nicht trauen, gehören in `choices`, nicht in `variables`

Im Template-Modus landet ein Wert in `variables` so im Prompt, wie er ist —
gemessen hat einer, der „ignoriere alle bisherigen Anweisungen" sagte, die
Antwort umgelenkt. Die `_limited`-Aufrufe nehmen stattdessen Paare
`{widget_id: value_id}`; freier Text, dort übergeben, hat den Prompt nicht
erreicht.

### Vorschlagen, nicht schreiben

Für alles, was ein Modell entschieden hat, führt der Weg über
`suggestions.propose(...)` und einen Menschen — nicht über `node.update(...)`.
Der Template-Modus der b-api schlägt genauso vor: `BapiTemplates.suggest` legt
offene Vorschläge an, und `repo.flows.accept_suggestion` übernimmt einen
(gemessen am 11.09.2026). Wo wirklich geschrieben werden soll: planen und den
Plan zeigen.

```python
# async: plan_update und apply() sind Koroutinen
plan = await plan_update(node, title=proposed)
print(plan.describe())        # alt -> neu, für einen Menschen
await plan.apply()            # erst nach der Bestätigung
```

### Eine Form für Erfolg und Fehlschlag

```python
# async: as_result nimmt ein Awaitable
outcome = await as_result(repo.flows.search(text))
outcome.ok, outcome.error_type      # False, "NotFoundError"
```

`error_type` lässt ein Werkzeug „anders formulieren hilft vielleicht" von
„Zugangsdaten fehlen" unterscheiden, ohne die Meldung zu zerlegen. Fehler
tragen keinen Java-Stacktrace.

### Adressen von einem Modell sind ungeprüft

`check_url` lehnt Loopback, Link-Local und private Bereiche ab.
`BildungsAPI.call` prüft seine Route Segment für Segment —
`"../../administration/account"` wird abgelehnt statt mit dem API-Schlüssel
gesendet.

### Was nie in ein Protokoll gerät

Header, Zugangsdaten, Query-Zeichenketten und der Pfad jeder Adresse, die der
Aufrufer übergeben hat. Protokolliert wird nur, was die Bibliothek selbst
gebaut hat.

---

## 7. Wo man nachschlägt

| Frage | Datei |
|---|---|
| was genau liefert dieser Aufruf | [`docs/REFERENCE.de.md`](../../../docs/REFERENCE.de.md) · [en](../../../docs/REFERENCE.md) |
| warum tut dieser Ablauf, was er tut | [`docs/FLOWS.de.md`](../../../docs/FLOWS.de.md) · [en](../../../docs/FLOWS.md) |
| wie ist die Bibliothek gebaut | [`docs/ARCHITECTURE.de.md`](../../../docs/ARCHITECTURE.de.md) · [en](../../../docs/ARCHITECTURE.md) |
| ein lauffähiges Beispiel | `docs/examples/01…23` — siehe die README-Tabelle |
| was sich geändert hat | `CHANGELOG.md` |

Fangen Sie mit `docs/examples/10_two_levels.py` an, wenn Sie sich für eine
Ebene entscheiden: es schreibt denselben Anwendungsfall zweimal und zählt die
Anfragen, die jede Fassung sendet.

---

## 8. Prüfliste, bevor ein Werkzeug damit ausgeliefert wird

```
[ ] Instanz kommt aus der Konfiguration, nicht aus einem Literal im Code
[ ] Zugangsdaten aus Umgebung oder Vault, nie im Quelltext, nie im Protokoll
[ ] Jedes Suchergebnis: `unresolved` geprüft und weitergereicht
[ ] Jede gemeldete Zahl: `total_is_lower_bound` beachtet
[ ] Jeder Gang: `truncated` / `complete` weitergereicht
[ ] Jeder Schreibvorgang: SilentDropError behandelt, nicht verschluckt
[ ] Text aus dem Repositorium mit `as_untrusted` umschlossen
[ ] URLs von einem Modell durch `check_url` geschickt
[ ] Vom Modell entschiedene Änderungen über `suggestions.propose`, nicht `update`
[ ] Fehler als `EduSharingError` gefangen, mit `error_type` gemeldet
```

---

## 9. Verwandte Skills

| Skill | Wofür |
|---|---|
| `wlo-edu-sharing-api` | die rohe REST-API, WLO-Datenmodell, Lizenzschlüssel, NGSearch |
| `wlo-environments` | welche Adresse Staging ist, welche Produktiv; Variablennamen |
| `wlo-metadata-agent-api` | die eigenen Endpunkte des Metadata Agent |
| `wlo-bapi-llm` / `wlo-b-api-llm` | Modellliste und Anbieterverhalten des Gateways |
| `wlo-suggestions-curation` | der redaktionelle Ablauf, den `suggestions` hier speist |
| `wlo-mcp-search` / `wlo-mcp-python-client` | einen MCP-Server darüber bauen |

Widersprechen jene Skills und dieser sich über einen *Python*-Aufruf, gewinnen
dieser und `docs/REFERENCE.de.md`. Widersprechen sie sich über eine *Adresse*,
einen *rohen Endpunkt* oder das WLO-Datenmodell, gewinnen jene.
