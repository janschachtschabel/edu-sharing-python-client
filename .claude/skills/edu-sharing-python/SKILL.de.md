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
```

Die drei Nachbardienste bekommen jeder **seine eigene** Adresse und haben
ebenfalls keine Voreinstellung — `from_env()` verweigert ohne die Variable,
statt Daten an einen Host zu schicken, den niemand gewählt hat:

| Dienst | Klasse | Variable |
|---|---|---|
| LLM-Gateway (b-api) | `BildungsAPI` | `B_API_BASE_URL` + `B_API_KEY` |
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
| alle Werte eines Feldes, oder eine Teilzeichenkette | `repo.vocab.values(prop)` / `repo.vocab.suggest(prop, "ysik")` |
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

### Redaktionelle Flächen (kein Ablauf — nur API-Ebene)

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

Die Tabellen oben weisen den Weg für die zwanzig häufigen Aufgaben. Alles
Übrige erreicht man über ein Objekt, das man ohnehin schon in der Hand hält.
Hier steht jedes öffentliche Glied beim Namen, damit nichts geraten werden
muss — die Argument- und Rückgabeformen stehen in `docs/REFERENCE.de.md`.

**Hinein**

| Man hält | Woher | Was darauf ist |
|---|---|---|
| `Repository` | `Repository(url, credential=…)` oder `.from_env()` | `.search()` `.node()` `.create_node()` `.children()` `.create_collection()` `.update_collection()` `.add_to_collection()` `.remove_from_collection()` `.find_collections()` `.resolve()` `.resolve_all()` `.about()` `.whoami()` `.metadatasets()` `.close()`; `.url` `.credential` `.metadataset` `.raw` `.flows` `.people` `.relations` |
| `AsyncRepository` | dasselbe, innerhalb einer Ereignisschleife | dieselben Namen mit `await`, `.aclose()` statt `.close()`, dazu `.nodes` `.collections` `.vocab` `.searcher` |
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
| `Collections` | `repo.collections` — **nur asynchron** | `.find()` `.create()` `.update()` `.add()` `.remove()` |
| `Nodes` | `repo.nodes` — **nur asynchron** | `.get()` `.create()` `.children()` `.repository_url`; `ChildPage`: `.nodes` `.total` `.offset` |
| `Search` | `repo.searcher` — **nur asynchron** | `.search()` |
| `Vocabulary` | `repo.vocab` — **nur asynchron** | `.values()` `.suggest()` `.resolve()` `.resolve_all()` `.clear_cache()`; `VocabularyValue`: `.uri` `.label` |
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
| `CuratedPage` | `node.page.get()` | `.collection_id` `.folder_id` `.variants` `.rendered_id` `.document` `.rendered` `.by_position` `.variant()` |
| `PageVariant` | `page.variant(…)`, `variant_from_node(…)` | `.id` `.title` `.is_template` `.target_group` `.educational_contexts` `.intention` `.education_levels` `.swimlanes` `.readable` `.node_ids` |
| `Swimlane` / `SwimlaneItem` | `variant.swimlanes` | `.heading` `.type` `.items` / `.widget` `.node_id` |
| `Ancestry` | `ancestry_of(…)`, `collections_of(…)` | `.node` `.parents` `.scope` |

**Die Nachbardienste als Objekte**

| Man hält | Woher | Was darauf ist |
|---|---|---|
| `BildungsAPI` | `BildungsAPI(url, key)` oder `.from_env()` | `.chat()` `.respond()` `.models()` `.load()` `.embeddings()` `.moderate()` `.images()` `.call()` `.aclose()` |
| `Answer` | `.chat()` / `.respond()` | `.text` `.status` `.reason` `.model` `.truncated` `.raw` |
| `Model` | `.models()` | `.id` `.name` `.demand` `.status` `.input` `.output` `.owned_by` `.shutdown_date` `.is_ready` `.can_chat` `.is_retired_on()` |
| `LoadReport` | `.load()` | `.provider` `.models` `.reports_load` `.retired` `.total` `.least_loaded` `.summary()`; freie Funktionen `load_report()` `rank_models()` `rank_among()` `pick_model()` `is_rankable()` |
| `Moderation` / `GeneratedImage` | `.moderate()` / `.images()` | `.flagged` `.categories` `.scores` / `.url` `.b64` `.revised_prompt` |
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
| eine Suche, die neu ordnet und beide Hälften meldet | `search_reranked(repo, text)` |
| jede Untersammlung einer Sammlung | `sub_collections(repo, id)` |
| die Bewertung eines Knotens, den man hält | `rating_of(node)` / `rate(…)` / `unrate(…)` |
| Text kürzen, bevor er ein Modell erreicht | `cap_text(text, max_chars)` |

**Fehler** — alle erben von `EduSharingError`; ein einziges
`except EduSharingError` fängt daher alles, was diese Bibliothek wirft:

`TransportError` · `AuthenticationError` · `PermissionDeniedError` ·
`NotFoundError` · `ValidationError` · `ConflictError` · `SilentDropError` ·
`ServerError` · `UnsafeUrlError`

`at_least(name, value, limit)` ist die Grenzprüfung, die die Clients auf ihre Einstellungen anwenden;
`details_withheld(…)` benennt, was ein Fehler bewusst nicht preisgibt.

**Der Rest von `__all__`** ist Maschinerie, die man nur anfasst, wenn man die
Bibliothek erweitert statt sie zu benutzen: `Flows` (der Typ hinter `repo.flows`),
`__version__`, die Konstruktoren `from_response` / `from_node` / `from_raw_header` /
`error_from_response`, die b-api-Rumpfhelfer `build_body` / `read_answer` /
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
| `DEFAULT_MAX_COLLECTIONS` / `DEFAULT_MAX_WIDGETS` | `50` / `24` | Obergrenzen für `browse_tree` und für eine gerenderte Seite |
| `RELATED_ON` | `("subject", "level")` | die Felder, auf die `related()` standardmäßig vergleicht |
| `METHODS` | `("simple", "browser")` | die Extraktionsverfahren, die `text_of` annimmt |
| `PROPOSAL_BATCH` | `"edusharing-python"` | unter welchem Stapelnamen Vorschläge abgelegt werden |
| `GERMAN` | ein `LanguageProfile` | die deutschen Stoppwort-, Rahmenwort- und Synonymlisten |

| Konstante | Wert | Warum sie einen Namen hat |
|---|---|---|
| `KEYWORD_PROPERTY` | `cclom:general_keyword` | die gemeinsame Schlagwortliste (siehe 4.6) |
| `CHILD_ASPECT` / `ORDER_PROPERTY` | `ccm:io_childobject` / `ccm:childobject_order` | was ein Kindobjekt kennzeichnet und ordnet |
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

Die Aufrufe zu kennen genügt nicht, um richtigen Code gegen ein Repositorium zu
schreiben. Diese acht Eigenschaften des darunterliegenden Speichers erklären das
meiste, was sonst wie ein seltsames Verhalten der Bibliothek aussieht.

### 4.1 Jeder Wert ist eine Liste

Eine Eigenschaft ist nie ein einzelner Wert. `node.properties` ist
`dict[str, list[str]]` — ein Titel ist eine einelementige Liste, ein Fach mit
drei Werten eine dreielementige, und eine fehlende Eigenschaft ist ein
fehlender Schlüssel, keine leere Zeichenkette.

```python
node.properties["cclom:title"]      # ["Bruchrechnung erklärt"] -- eine Liste
node.get("cclom:title")             # "Bruchrechnung erklärt"   -- der erste Wert
node.get_all("ccm:taxonid")         # alle Werte, [] wenn ungesetzt
```

`get()`, wenn man einen will; `get_all()`, wenn das Feld berechtigt mehrere
tragen kann. Direkt in `properties` zu greifen und das Ergebnis wie eine
Zeichenkette zu behandeln ist der mit Abstand häufigste Fehler.

### 4.2 Vier Namensräume, und sie bedeuten Verschiedenes

| Präfix | Kommt aus | Beispiel |
|---|---|---|
| `cm:` | Alfrescos eigenem Inhaltsmodell — dem Dateisystem darunter | `cm:name`, `cm:title`, `cm:description` |
| `cclom:` | dem Metadatenstandard für Lernobjekte | `cclom:title`, `cclom:general_keyword`, `cclom:general_description` |
| `ccm:` | edu-sharings eigenen Ergänzungen | `ccm:taxonid`, `ccm:educationalcontext`, `ccm:wwwurl` |
| `virtual:` | nicht aus dem gespeicherten Modell — ein Dienst legt sie auf die Antwort | `virtual:profiling_widget_intention` |

Zwei Folgen daraus. Eine unter `ccm:` erfundene Eigenschaft existiert für den
Metadatensatz nicht (siehe 4.5). Und ein zurückgelesener `virtual:`-Wert gehört
dem Dienst, der ihn erzeugt hat — bei redaktionellen Seiten dem Seitenbaukasten
—, ist also zum Lesen da und über das zuständige Werkzeug zu ändern.

### 4.3 `cm:name` ist ein Schlüssel, kein Titel

`cm:name` ist der Name des Knotens **innerhalb seines Elternordners** — das
Gegenstück zu einem Dateinamen. Er muss unter den Geschwistern eindeutig sein,
und das Repositorium weist Zeichen zurück oder verstümmelt sie, die ein
Dateiname nicht tragen kann. Der lesbare Titel ist ein anderes Feld.

```python
name_from_title("Bruchrechnung: Übung 1/2")   # ein zulässiger cm:name
```

Schlimmer: das Titelfeld ist nicht überall dasselbe. **Material trägt
`cclom:title`, eine Sammlung trägt `cm:title`.** Wer das falsche schreibt,
hinterlässt ein scheinbar titelloses Objekt. Die Kurzform `title=` der
Bibliothek schreibt beide — ihr also den Vorzug geben, statt die Eigenschaft
selbst zu benennen.

### 4.4 Vokabularfelder tragen URIs, nie Labels

In `ccm:taxonid` steht nicht `"Biologie"`, sondern eine URI aus einem
SKOS-Vokabular. Ein Label zu filtern oder zu schreiben setzt einen Wert ein,
der auf nichts passt.

```python
await repo.vocab.resolve_all("subject", "Biologie")
# -> beide URIs: das Schulfach und das Hochschulfach
```

Ein Label kann zu zwei Vokabularen gehören — gegen die Staging gemessen tragen
25 Fach-Labels denselben Namen einmal unter den Schulfächern und einmal unter
der Hochschulfächersystematik. Darum gibt `resolve_all` eine Liste zurück und
die Suche filtert auf alle; nur den ersten zu nehmen findet das halbe Material.

### 4.5 Der Metadatensatz entscheidet, was es gibt — stillschweigend

Jede Instanz trägt einen oder mehrere Metadatensätze (`repo.metadatasets()`),
die festlegen, welche Eigenschaften ein Objekt haben darf. Eine Eigenschaft,
die der Satz nicht kennt, wird **nicht** zurückgewiesen: das Repositorium
antwortet `200 OK` und speichert nichts.

Darum liest jeder Schreibvorgang dieser Bibliothek zurück und wirft bei
Abweichung `SilentDropError`. Das nicht abschalten — und eine `200` nicht als
Beleg nehmen.

### 4.6 Manche Listen sind gemeinsames Eigentum

`cclom:general_keyword` wird gemeinsam gepflegt — von Redaktionen, von Crawlern,
von anderen Anwendungen. Wer es setzt, ersetzt die Arbeit aller anderen.

```python
await node.add_keywords("Bruchrechnung")        # ergänzt
await node.update(keywords=["Bruchrechnung"])   # ersetzt -- selten gewollt
```

Dieselbe Vorsicht gilt für jedes listenwertige Feld, das man nicht allein
verfasst hat.

### 4.7 Aspekte sind keine Typen

Ein Knoten hat einen Typ (`ccm:io` für Material, `ccm:map` für eine Sammlung)
und beliebig viele darübergelegte Aspekte. Ein Kindobjekt ist kein eigener
Knotentyp — es ist ein gewöhnlicher Knoten mit dem Aspekt
`ccm:io_childobject`. Wer danach als Typ sucht, findet nichts.

### 4.8 Eigenschaften kommen leer, wenn man sie nicht anfordert

Mehrere Repositoriums-Routen liefern Knoten mit leerer `properties`-Abbildung,
solange die Anfrage kein `propertyFilter=-all-` trägt. Die Bibliothek setzt es,
wo sie diese Routen aufruft; wer sie mit `repo.raw.request(...)` umgeht, muss es
selbst setzen — sonst hält man für fehlend, was bloß nicht angefordert war.

---

## 5. Die Fallen — worauf zu achten ist

Jede davon wurde gegen eine echte Instanz gemessen. Sie sind der Grund, warum
es diese Bibliothek gibt.

### 5.1 HTTP 200 heißt nicht, dass etwas gespeichert wurde

edu-sharing nimmt Schreibvorgänge an, die es dann verwirft. Jeder
Schreibvorgang dieser Bibliothek liest zurück und wirft `SilentDropError`,
statt Erfolg zu melden.

```python
try:
    await node.update(title="Neu")
except SilentDropError as exc:
    exc.dropped        # {"cclom:title": ["Neu"]}
```

**Wer über `repo.raw` schreibt, verliert das.** Dann selbst zurücklesen.

Bekannte Verwerfer: `relations.create(metadata=...)` (angenommen, nirgends
gespeichert) und Metadatensatz-Felder, die die Instanz nicht kennt.

### 5.2 `unresolved` ist keine Zierde

Ein Filterwert, den die Instanz nicht kennt, wird **nicht angewendet** — und
die Suche beantwortet eine weitere Frage als die gestellte.

```python
answer = await repo.flows.search("Zellen", subject="Bio")
answer["unresolved"]   # [{"field": "subject", "value": "Bio",
                       #   "suggestions": ["Biologie"]}]
```

Beim Schreiben genauso: `add_material` und `update_material` liefern
`unresolved` für Werte, die **nicht** geschrieben wurden. Das Material gibt es
dann ohne sie.

**Nie ein Ergebnis an einen Menschen oder ein Modell melden, ohne das geprüft
zu haben.**

### 5.3 `total_is_lower_bound`, `truncated`, `complete`

- `total_is_lower_bound=True` → `total` zählt *mindestens* so viele. Wer das
  als genaue Zahl meldet, behauptet eine Zahl, die keine ist.
- `browse_tree`/`search_in_collection`: `truncated=True` → der Gang hat früh
  abgebrochen. Ein leeres Ergebnis heißt dann **nicht** „es gibt keins".
- `collection_stats`: `complete=False` → die Aufschlüsselung ist eine
  Stichprobe.

`find_collections` setzt `total_is_lower_bound` immer: es führt zwei Routen
zusammen.

### 5.4 Eine Sammlung ist kein Ordner, und eine Suche lässt sich nicht darauf einschränken

- Sammlungen über `repo.create_collection` anlegen, nie als `ccm:map`-Knoten.
  Ein anders angelegter Knoten ist für den Rest des Systems keine Sammlung.
- Sammlungen bilden einen **Graphen**, keinen Baum — eine Sammlung kann
  mehrere Eltern haben. `browse_tree` sichert gegen Zyklen und sagt es über
  `truncated`.
- Es gibt keine auf eine Sammlung eingeschränkte Suche.
  `virtual:primaryparent_nodeid` antwortet mit HTTP 400, und es wäre ohnehin
  die falsche Antwort: eine kuratierte Sammlung hält *Referenzen* auf Knoten,
  deren primärer Elternteil woanders liegt. `search_in_collection` läuft ab und
  filtert lokal.
- `collection_contents` fragt **zwei** Routen. Nur das Material zu holen ließe
  eine Sammlung aus Untersammlungen leer aussehen.

### 5.5 Drei verschiedene Arten von Zugehörigkeit

| | Hält | Gelesen mit |
|---|---|---|
| Sammlung | Referenzen auf Material, das auch anderswo liegt | `collection_contents` |
| Serienobjekt | ein Dokument *unter* einem Material, ohne eigenes Leben | `child_objects` |
| Beziehung | zwei Materialien, die *nebeneinander* stehen | `relations` |

Ein Serienobjekt trägt seinen Dateinamen in `name` und ein **leeres** `title`.
Jeder andere Ablauf zeigt `title` an, wer hier danach greift, sieht nichts.

Beziehungen pflegen die Gegenrichtung automatisch: `isPartOf` von der Folge
angelegt, und die Reihe meldet `hasPart`. Eine frische Beziehung ist
`approved=False` — `relations.approve(...)` setzt es.

### 5.6 Labels gegen URIs

`node.get("ccm:taxonid")` gibt die URI. `node.labels("ccm:taxonid")` gibt
„Mathematik". `SearchHit.labels` tut dasselbe. Die Ablauf-Ebene löst die Labels
in `fields` für Sie auf.

Facetten*werte* sind URIs und tragen kein Label — `FacetValue` hat nur `value`
und `count`.

Welche Kurznamen (`subject`, `level`, …) es gibt, wird **von der Instanz
gelesen**, nicht in der Bibliothek festgelegt: `repo.searcher.field_aliases`.

**Ein Label kann zu zwei Vokabularen gehören.** Am 31.08.2026 gegen die Staging
gemessen: 25 Fachlabels stehen sowohl in `discipline` (Schulfächer) als auch in
`hochschulfaechersystematik` (Hochschulfächer) — darunter `Biologie`, `Chemie`,
`Physik`. Eine Suche über das Label filtert auf **alle**, denn die halbe
Materialmenge zu finden und wie die ganze auszusehen ist eine falsche Antwort:

```python
await repo.vocab.resolve(prop, "Biologie")      # die erste — eine von zweien
await repo.vocab.resolve_all(prop, "Biologie")  # beide, so filtert die Suche
```

Geschrieben wird die erste, und zwar mit Absicht: ein Arbeitsblatt für Klasse 6
als Hochschulfach zu markieren ist eine Behauptung, keine Erweiterung. Wer die
Hälften trennen will, filtert zusätzlich nach `level`.

### 5.7 Blättern, Grenzen und Vorgaben, die stillschweigend kürzen

- `repo.people.members(group)` hat die Vorgabe 10 und kürzt, ohne es zu sagen.
  `limit` mitgeben.
- `collection_contents` braucht `propertyFilter=-all-`, um überhaupt
  Eigenschaften zu bekommen; die Bibliothek setzt es. Über `repo.raw` müssen
  Sie es selbst setzen.
- Die zwei Methoden des Extraktionsdienstes sind **nicht** gereiht: gemessen
  lieferte `simple` einen Artikel, wo `browser` ein Cookie-Banner lieferte.
  Bringt eine nichts, ist die andere der zweite Versuch.

### 5.8 Ein Rahmenwort ruiniert eine Anfrage

Über einen Pool von 60 Knoten gemessen: `"Bruchrechnung"` traf 0 Knoten,
`"die Bruchrechnung"` traf 43. `rerank=True` weitet die Anfrage auf und bewertet
neu; das kostet mehrere Anfragen, also dafür, wenn die Anfrage von einem
Menschen oder einem Modell kommt, nicht für eine maschinell gebaute
Filteranfrage.

`rerank=True` und `offset` vertragen sich nicht — der Pool wird über die
Varianten zusammengeführt, ein Versatz darin bedeutete also nicht, was ein
Aufrufer erwartet.

### 5.9 Tote Indexeinträge

Gemessen: 4 von 25 Suchtreffern waren nicht mehr abrufbar. `describe_many`
meldet sie in `failed`, statt zu werfen — eine kürzere Liste als angefragt ist
so davon zu unterscheiden, dass es diese Knoten nicht gibt.

### 5.10 Die zwei Anbieter sind nicht austauschbar

Gemessen am 31.08.2026. `openai` bietet 132 Modelle und meldet keine
Auslastung; `academiccloud` bietet 15 und meldet `demand` 0 bis 23, was sich im
Minutentakt ändert. Beide haben `chat/completions` und `responses`. Nur OpenAI
hat `embeddings`, `moderations` und `images/generations` — die AcademicCloud
antwortet 404, und ihre Modelle erzeugen `text` und `thought`, sonst nichts.

`reasoning_effort` und `verbosity` wirken bei der gpt-5- und o-Serie und werden
von älteren OpenAI-Modellen mit 400 abgelehnt. Die AcademicCloud nimmt sie an
und ignoriert sie: gleicher Tokenverbrauch bei `low` und `high`. Ihr Hebel ist
`chat_template_kwargs`, das die Bibliothek für Qwen3 setzt.

Die Bibliothek stellt beide auf `low` und wendet sie nur an, wo sie wirken.
**Ein ausdrücklicher Wert wird nie für Sie verworfen** — er löst stattdessen
einen Fehler aus, denn eine Antwort ohne den gewünschten Aufwand sieht genauso
aus wie eine mit ihm.

Ein virtuelles Modell (`model=["a","b","c"]` oder ein Name aus
`virtual_models`) nimmt das am wenigsten ausgelastete davon. Das lohnt bei der
AcademicCloud; bei OpenAI wird daraus eine Ausweichkette in Ihrer Reihenfolge.

### 5.11 Auslastung abfragen, und wechseln statt warten

`demand` ändert sich im Minutentakt, deshalb wird die Modellliste 30 Sekunden
gemerkt. Stellen Sie das darauf ein, wie lange Ihr Prozess lebt:

```python
# Ein Skript, das eine Minute läuft: einmal fragen.
api = BildungsAPI.from_env(models_cache_seconds=CACHE_FOREVER)
print((await api.load()).summary())      # ins Startprotokoll

# Ein Dienst, der einen Tag läuft: die 30 Sekunden stehen lassen. CACHE_FOREVER
# ließe ihn nach Zahlen von vor Stunden entscheiden.
```

`load()` liefert einen `LoadReport`. **Zuerst `reports_load` lesen** — bei
OpenAI steht dort `false`, es wird gar keine Auslastung gemeldet, und die
Rangfolge ist alphabetisch statt eine Aussage über Warteschlangen.

**Wechseln schlägt Warten, solange es wohin zu wechseln gibt.** Ein 503 ist
wiederholbar, also verbrauchte ein ausgelastetes Modell bisher das volle
`max_retries` — rund 17 s bei voreingestellter Wartezeit — während ein anderes
danebenstand. Ein Kandidat bekommt jetzt `retries_before_switching`
Wiederholungen (Vorgabe 1), solange ein weiterer da ist; der letzte behält das
volle Budget. `max_retries=0` heißt weiterhin genau ein Versuch je Modell: die
Stellschraube senkt nur.

Ein 429 ist der Fall, dem das nicht hilft — die AcademicCloud begrenzt den
Schlüssel, nicht das Modell, der nächste Kandidat scheitert also genauso
schnell.

### 5.12 Am blockierenden `Repository` sind vier Zugänge weiterhin asynchron

`Repository` hüllt das meiste, was es herausgibt, so ein, dass es blockiert.
Vier Eigenschaften nicht: `repo.vocab`, `repo.searcher`, `repo.collections` und
`repo.nodes` geben die asynchronen Objekte unverändert zurück. Ein Methoden-
aufruf darauf erzeugt aus blockierendem Code eine Koroutine, die nie erwartet
wird — kein Fehler, keine Wirkung.

```python
repo = Repository(url, credential=cred)
repo.collections.find("Bruchrechnung")   # ein Koroutinen-Objekt -- tut nichts
repo.find_collections("Bruchrechnung")   # der blockierende Weg
```

Zu jedem gibt es ein blockierendes Gegenstück am Repositorium selbst:

| Statt | Nimm |
|---|---|
| `repo.nodes.get/create/children` | `repo.node()` / `repo.create_node()` / `repo.children()` |
| `repo.collections.find/create/update/add/remove` | `repo.find_collections()` / `repo.create_collection()` / `repo.update_collection()` / `repo.add_to_collection()` / `repo.remove_from_collection()` |
| `repo.searcher.search` | `repo.search()` |
| `repo.vocab.resolve` / `.resolve_all` | `repo.resolve()` / `repo.resolve_all()` |
| `repo.vocab.values` | `repo.flows.vocabulary(field)` |

`repo.vocab.suggest` und `repo.vocab.clear_cache` haben kein blockierendes
Gegenstück; alles, was ein Aufrufer zum Filtern braucht, schon.

---

### 5.13 Ein Sammlungs-Listing liefert Referenz-IDs

Eine Sammlung hält **Referenzen**, keine Datensätze. `collection_contents`,
`search_in_collection` und jedes auf eine Sammlung bezogene Listing geben die
IDs dieser Referenzen zurück — der gewöhnliche Weg zu einer ID, kein
Sonderfall. Gegen Staging gemessen (02.09.2026): `/usage` antwortet einer
Referenz-ID mit leerer Liste und dem Original mit zwei Sammlungen; und ein
Schreibvorgang an eine Referenz wird auf der Referenz gespeichert und erreicht
den Datensatz nie (vom MCP am 17.08.2026 gemessen) — die Rückleseprobe merkt
es nicht, weil sie denselben Knoten liest.

Die Bibliothek löst das auf. `node.original_id` nennt den Datensatz (`None`
auf einem Original), `node.collections()` und `flows.placement` fragen für das
Original, und `update()`, `set_property()` und `add_keywords()` schreiben
dorthin und geben das **Original** mit gesetztem `redirected_from` zurück.
Löschen wird *nicht* umgeleitet: an einer Referenz verschwindet nur die
Referenz, das ist harmlos, und `flows.delete` sagt `is_reference`, damit klar
ist, welches von beiden ging.

```python
node = await repo.node(node_id=listing_id)
node.is_reference            # True
changed = await node.update(title="…")
changed.id                   # die ID des Originals, nicht listing_id
changed.redirected_from      # listing_id -- der Schreibvorgang wurde umgeleitet
```

---

### 5.14 Ein Skill ist ein Datensatz mit Inhaltsart — und der Metadatensatz entscheidet, ob man danach filtern kann

Skills sind gewöhnliche Datensätze, deren Inhaltsart „Anleitung" sagt und
deren angehängte Datei die `SKILL.md` ist. Gegen Staging gemessen
(02.09.2026): mit `mds_oeh` ist die Inhaltsart ein Suchkriterium und 34
Skills antworten; mit `-default-` weist das Repositorium das Kriterium zurück
(`ValidationError`, und die Meldung sagt warum). `EDU_SHARING_METADATASET=
mds_oeh` setzen oder `metadataset=` übergeben — `from_env()` liest die
Variable seit dem 02.09.2026.

Zwei weitere gemessene Fallen: die `SKILL.md` liest man mit `download()`,
weil `/textContent` für Markdown leer ist; und der Ordner eines Skills (seine
Begleitdateien) antwortete anonym mit 403 — `files_reason` sagt es, statt eine
leere Liste als „reist allein" auszugeben.

Alles, was eine Konvention benennt — die URIs der Inhaltsarten, wie ein
Registry-Dokument sich zu erkennen gibt, die Blockarten — ist
`SkillConventions`, ein Parameter mit WLOs `WLO_SKILLS` als Vorgabe. Ein
anderes Repositorium übergibt seine eigenen. Und das zurückkommende Markdown
ist hochgeladener Inhalt: vor dem Prompt mit `as_untrusted` rahmen.

```python
repo = AsyncRepository(url, metadataset="mds_oeh")
found = await repo.flows.find_skills("Fragen generieren")
doc = await repo.flows.skill(found["hits"][0]["id"])
doc["files_reason"]          # anonym "folder_unreadable"
```

### 5.15 Ein Datensatz ist nicht in dem Moment auffindbar, in dem er angelegt wurde

Der Suchindex hinkt dem Knotenspeicher nach. Gemessen auf Staging (02.09.2026):
ein per `add_material` angelegter Datensatz war über seine Adresse
(`find_by_url`, `ccm:wwwurl`) nach 5,3 Sekunden auffindbar, vorher nicht. Die
Dublettenprüfung in `add_material` kann also einen Datensatz, den derselbe
Prozess eben angelegt hat, nicht sehen, und `search` listet ihn noch nicht —
`repo.node(node_id)` schon, denn das liest den Knotenspeicher. Ein Import, der
dieselbe Adresse zweimal enthält, muss seine Eingabe selbst entdoppeln; ein
Test, der anlegt und dann sucht, muss warten.

---

## 6. Hinter ein Modell stellen

### Text aus dem Repositorium darf nie als Anweisung wirken

Beschreibungen, Titel und Kommentare schreiben Fremde. Vor dem Modellkontext
umschließen:

```python
from edusharing.agent import as_untrusted, sanitize_text

as_untrusted(hit.description, label="description")
```

### Vorschlagen, nicht schreiben

Für alles, was ein Modell entschieden hat, führt der Weg über
`suggestions.propose(...)` und einen Menschen — nicht über `node.update(...)`.
Wo wirklich geschrieben werden soll: planen und den Plan zeigen.

```python
plan = await plan_update(node, title=proposed)
print(plan.describe())        # alt -> neu, für einen Menschen
await plan.apply()            # erst nach der Bestätigung
```

### Eine Form für Erfolg und Fehlschlag

```python
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
| ein lauffähiges Beispiel | `docs/examples/01…17` — siehe die README-Tabelle |
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
