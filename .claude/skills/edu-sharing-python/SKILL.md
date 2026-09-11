---
name: edu-sharing-python
description: Using the edu-sharing-python-client library (import `edusharing`) — both levels (API objects and flow dicts), every flow, the whole public surface, how edu-sharing stores metadata (list values, the cm:/cclom:/ccm:/virtual: namespaces, cm:name vs cclom:title, vocabulary URIs, metadata sets), the neighbouring services (b-api LLM gateway as proxy and with prompt templates; text extraction; metadata agent), the measured traps, and putting it behind a model. Use when writing Python against edu-sharing, building an MCP server or agent tool over WLO/OpenEduHub content, or when a call returned HTTP 200 and stored nothing. Trigger u.a. "edu-sharing Python", "edusharing library", "repo.flows", "SilentDropError", "Bibliothek nutzen", "Material anlegen Python", "MCP-Werkzeug edu-sharing", "b-api Python", "BapiTemplates", "KI-Vorschläge", "Textextraktion", "metadata agent schema", "welcher Aufruf für", "unresolved", "total_is_lower_bound", "propertyFilter", "Metadatensatz", "properties leer", "Eigenschaft schreiben".
---

# edu-sharing for Python — how to use it

*Deutsche Fassung: [SKILL.de.md](SKILL.de.md)*

The library at `github.com/janschachtschabel/edu-sharing-python-client` (package
`edu-sharing-python-client`, import `edusharing`). It wraps edu-sharing's REST
API and three neighbouring services, and its central promise is that **a write
that did not happen is reported as a failure, not a success**.

**This skill covers the library.** For the raw REST API, WLO's own data model
(Quelldatensatz, Spider, replicationsource), licence keys or NGSearch body
fields, use `wlo-edu-sharing-api`. For instance addresses and environment
variable names, use `wlo-environments`. Those are the source of truth for
*deployment*; this one is the source of truth for *the Python surface*.

Written in English because the library's code and identifiers are English --
this is the version a model loads. [`SKILL.de.md`](SKILL.de.md) is the same
routing table for people who would rather read German; both are held to the
same tests, so neither can quietly omit a flow or invent a call.

---

## 1. Orientation in sixty seconds

```bash
uv pip install -e .        # not on PyPI yet
```

```python
from edusharing import Repository

with Repository("https://repository.staging.openeduhub.net") as repo:
    result = repo.search("Bruchrechnung", limit=5)
    for hit in result.hits:
        print(hit.title, hit.url)
```

Two levels, both permanent:

| | API level | Flow level |
|---|---|---|
| Reached as | `repo.search(...)`, `repo.node(...)` | `repo.flows.search(...)` |
| Returns | objects — `SearchResult`, `Node` | plain `dict`, ready for `json.dumps` |
| Good for | writing Python against edu-sharing | handing the answer on |
| Requests | one endpoint per call | one call, several endpoints |

**Rule of thumb:** if the result goes to a model, an MCP tool or an HTTP
response, use `repo.flows`. If you are writing the calling code yourself, use
the API level.

`Repository` is blocking. `AsyncRepository` is the same surface with `await`.
Use the async one inside an event loop, the blocking one everywhere else.

---

## 2. The instance is always a parameter

**Never hardwire an address.** The library has no default instance; every entry
point takes one, and no call below it takes an address of its own.

```python
repo = Repository(os.environ["EDU_SHARING_URL"], auth=(user, password))
repo = Repository.from_env()      # EDU_SHARING_URL / _USER / _PASSWORD
# user:password@ inside the URL is refused -- auth= or the environment carry them
```

The three neighbouring services each take **their own** address and also have
no default — `from_env()` refuses without the variable rather than sending data
to a host nobody chose:

| Service | Class | Variable |
|---|---|---|
| LLM gateway (b-api) | `BildungsAPI` | `B_API_BASE_URL` + `B_API_KEY` |
| the same gateway, template mode | `BapiTemplates` | `B_API_BASE_URL` + `B_API_KEY` + `EDU_SHARING_METADATASET` |
| Text extraction | `TextExtraction` | `EDU_SHARING_TEXT_EXTRACTION_URL` |
| Metadata agent | `MetadataAgent` | `METADATA_AGENT_URL` |

Which concrete addresses belong to staging and production is **not** in this
skill and not in the library — see `wlo-environments`.

---

## 3. Which call answers which question

The complete list with input and output shapes is
[`docs/REFERENCE.md`](../../../docs/REFERENCE.md) /
[`docs/REFERENCE.de.md`](../../../docs/REFERENCE.de.md). This is the routing
table.

*(File links here are relative to the library's checkout. Copied into
`~/.claude/skills/` they name paths in that repository, not on disk.)*

### Finding things

| The task | The call |
|---|---|
| search material | `repo.flows.search(text, subject=…, limit=…, exclude_ids=…, properties=…)` |
| search material *and* collections at once | `repo.flows.search_all(text)` |
| find collections only — by subject, or below one collection | `repo.flows.find_collections(text, subject=…, parent_id=…)` → read `unjudged` |
| which **skills** fit a task, or are filed in a collection | `repo.flows.find_skills(text, subject=…, collection_id=…)` — needs the metadata set that knows the content type |
| the best skill, loaded, with the runners-up | `repo.flows.pick_skill(text)` → read `reason` |
| more like this node | `repo.flows.related(node_id, on=["subject", "level"])` |
| which values does a field allow | `repo.flows.vocabulary("subject")` |
| every value of a field, or a substring of one | `repo.vocab.values(prop)` / `repo.vocab.suggest(prop, "ysik")` — `values` is cached for `DEFAULT_CACHE_SECONDS` (1 h) |
| ask again for unknown filter labels | at most `SUGGEST_LOOKUP_MAX` (10) of them get suggestions; the rest are reported without |
| a label's filter value — **all** of them | `repo.vocab.resolve_all(prop, "Biologie")` |
| a poorly phrased query ("something about fractions") | `repo.flows.search(text, rerank=True)` |
| search *inside* one collection | `repo.flows.search_in_collection(collection_id, query)` |
| find collections that render a curated page | `repo.flows.find_pages(text)` |

### Reading one thing

| The task | The call |
|---|---|
| everything about a node, as JSON | `repo.flows.describe(node_id)` |
| several nodes at once | `repo.flows.describe_many(node_ids)` |
| where does it sit (breadcrumb) | `repo.flows.placement(node_id)` |
| what is in this collection | `repo.flows.collection_contents(collection_id)` |
| what hangs *under* this material | `repo.flows.child_objects(node_id)` |
| what stands *beside* it | `repo.flows.relations(node_id)` |
| what is underneath, recursively | `repo.flows.browse_tree(collection_id, depth=2)` |
| how much is in there | `repo.flows.collection_stats(collection_id)` |
| the curated landing page | `repo.flows.page(collection_id)` |
| the text of a material, wherever it is — and *why* there is none | `repo.flows.text(node_id, extraction=…)` → read `source`, `reason` |
| a skill's instruction, its references and companion files | `repo.flows.skill(node_id)` → read `files_reason` |
| which skills a collection has approved, by working context | `repo.flows.skill_registry(collection_id, context=…)` → read `reason`, `context_match` |
| the file itself | `node.content.download()` / `node.content.text()` |
| the curated page as objects | `node.page.get()` / `node.page.render(variant)` |
| one page of a node's children | `repo.nodes.children(node_id, limit=…)` |
| who am I, what does this instance offer | `repo.whoami()` / `repo.about()` / `repo.metadatasets()` |
| text of a page the repository does *not* hold | `TextExtraction.text_of(url)` |

### Changing things

| The task | The call |
|---|---|
| create material with vocabulary | `repo.flows.add_material(title, url=…, subject=…)` · `if_exists=\"return\"` names an existing record for `url` instead of creating a second (`created`, `existing`) |
| change material | `repo.flows.update_material(node_id, title=…)` |
| build a collection and fill it | `repo.flows.build_collection(title, node_ids=[…])` |
| put existing material into a collection | `repo.add_to_collection(collection_id, node_id)` |
| the collection accessor behind those shortcuts | `repo.collections.find/create/update/add/remove` |
| take it out again (material stays) | `repo.remove_from_collection(collection_id, node_id)` |
| delete | `repo.flows.delete(node_id)` |
| upload a file | `node.content.upload(data, filename=…, mimetype=…)` |
| attach an answer sheet | `node.children.add(data, filename=…, mimetype=…)` |
| link two materials | `repo.relations.create(a, "isPartOf", b)` |
| make it publicly readable | `node.permissions.publish()` |
| keywords | `node.add_keywords([...])` / `node.remove_keywords([...])` |

### Editorial surfaces (API level, except accepting a proposal)

| The task | The call |
|---|---|
| comment | `node.comments.add(text)` / `.list()` / `.edit()` / `.delete()` |
| rate | `node.rate(4)` / `node.unrate()` |
| **propose** a value instead of writing it | `node.suggestions.propose(prop, value, reason)` |
| accept or reject a proposal | `node.suggestions.decide(ids, accept=True)` |
| **accept** a proposal so that it takes effect — write, read back, then mark | `repo.flows.accept_suggestion(node_id, suggestion_id)` → read `applied` |
| hand on for review | `node.workflow.submit("GROUP_redaktion", "TO_BE_CHECKED")` |
| grant or revoke rights | `node.permissions.grant(who, "Read")` / `.revoke(...)` |
| groups and members | `repo.people.memberships()` / `.group(name)` / `.members(name, limit=…)` / `.create_group(name)` / `.add_member(group, who)` |

### The neighbouring services

| The task | The call |
|---|---|
| ask a model | `BildungsAPI.chat(prompt)` |
| ask through the responses route | `.respond(prompt, model=…)` → check `.truncated` |
| the least loaded of several models | `.chat(prompt, model=["a", "b", "c"])` |
| what the models look like right now | `.load()` → `.summary()` |
| which models are there | `.models()` |
| cheaper thinking (default) | nothing — `reasoning_effort` is already `low` |
| more thinking | `.chat(prompt, reasoning_effort="high")` |
| embeddings *(OpenAI only)* | `.embeddings(texts)` |
| moderation *(OpenAI only)* | `.moderate(texts)` |
| image generation *(OpenAI only)* | `.images(prompt)` |
| any other forwarded OpenAI route | `.call("batches", body)` |
| a prompt kept on the server, filled from a node | `BapiTemplates.chat(configs, context_node_id=…)` |
| … with input you do not trust | `.chat_limited(configs, context_node_id=…, choices=…)` |
| have the model propose metadata, stored as suggestions | `.suggest(configs, widgets, context_node_id=…)` → take one over with `repo.flows.accept_suggestion` |
| question–answer pairs for a node *(experimental, stored)* | `.qas(node_ids)` — needs Write for the gateway's own account |
| text behind a URL | `TextExtraction.text_of(url, method="simple")` |
| what belongs in a content type's JSON | `MetadataAgent.content_types()` / `.schema(file)` |

### Building blocks for AI use

| The task | The call |
|---|---|
| one shape for success and failure | `as_result(awaitable, format=format_results)` → `ToolResult`: `.ok` `.text` `.data` `.error` `.error_type` `.metadata` |
| a hit as compact text | `format_hit(hit)` / `format_results(result)` |
| mark foreign text as data | `as_untrusted(text, label="description")` |
| clean control characters out | `sanitize_text(text)` / `one_line(text)` |
| refuse an internal address | `check_url(url)` / `is_safe_url(url)` |
| plan a change, let a person confirm | `plan_update(node, title=…)` → `ChangePlan`: `.node` `.changes` `.unchanged` `.has_changes` `.can_write` `.describe()` `.apply()` |

### The whole surface, object by object

The tables above route the common jobs. Everything else is reached
through an object you already hold. This names every public member, so nothing
has to be guessed — argument and return shapes are in `docs/REFERENCE.md`.

**Getting in**

| You hold | From | On it |
|---|---|---|
| `Repository` | `Repository(url, auth=…)` or `.from_env()` | `.search()` `.node()` `.create_node()` `.children()` `.create_collection()` `.update_collection()` `.add_to_collection()` `.remove_from_collection()` `.find_collections()` `.resolve()` `.resolve_all()` `.about()` `.whoami()` `.metadatasets()` `.close()`; `.url` `.credential` `.metadataset` `.raw` `.flows` `.people` `.relations` `.nodes` `.collections` `.vocab` `.searcher` |
| `AsyncRepository` | the same, inside an event loop | the same names awaited, `.aclose()` for `.close()` |
| `Credential` | `BasicCredential(user, pw)`, `BasicCredential.from_env()`, `AnonymousCredential()`, `credential_from(…)` | `.headers()` `.is_anonymous` `.username` |

**One node and everything hanging off it**

| You hold | From | On it |
|---|---|---|
| `Node` | `repo.node(node_id)`, `repo.create_node(…)` | read `.id` `.name` `.title` `.type` `.aspects` `.original_id` `.is_reference` `.redirected_from` `.url` `.access` `.can_write` `.is_public` `.preview_url` `.properties` `.keywords` `.raw` `.get()` `.get_all()` `.labels()` `.parents()` `.collections()`; write `.update()` `.set_property()` `.add_keywords()` `.remove_keywords()` `.rate()` `.unrate()` `.delete()`; doors `.content` `.children` `.permissions` `.workflow` `.comments` `.suggestions` `.page` `.rating` |
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

**Collections, people, relations, vocabulary**

| You hold | From | On it |
|---|---|---|
| `Collections` | `repo.collections` — blocking on `Repository` too, since 2026-09-10 | `.find()` `.create()` `.update()` `.add()` `.remove()` |
| `Nodes` | `repo.nodes` — blocking on `Repository` too, since 2026-09-10 | `.get()` `.create()` `.children()` `.repository_url` `.wrap(data)`; `ChildPage`: `.nodes` `.total` `.offset` |
| `Search` | `repo.searcher` — blocking on `Repository` too, since 2026-09-10 | `.search()` |
| `Vocabulary` | `repo.vocab` — blocking on `Repository` too, since 2026-09-10 | `.values()` `.suggest()` `.resolve()` `.resolve_all()` `.clear_cache()`; `VocabularyValue`: `.uri` `.label` |
| `People` | `repo.people` | `.memberships()` `.group()` `.members()` `.create_group()` `.delete_group()` `.add_member()` `.remove_member()`; `Group`: `.name` `.short_name` `.display_name` `.type` `.signup`; `Member`: `.name` `.is_group` |
| `Skills` | `repo.skills` | `.search()` `.get()` `.registry()` `.pick()`; `SkillConventions`: `.type_property` `.skill_type` `.registry_type` `.registry_mark` `.markdown_mimetypes` `.block_kinds`; `WLO_SKILLS` |
| `SkillSummary` / `SkillDocument` | `.search().hits` / `.get()` | `.id` `.original_id` `.title` `.description` `.keywords` `.url` `.download_url`; the document adds `.content` `.references` `.files` `.files_reason` `.folder_file_count`; `SkillFile`: `.id` `.title` `.mimetype` `.size` `.download_url`; `SkillSearch`: `.hits` `.unresolved` `.truncated` |
| `SkillRegistry` | `repo.skills.registry(collection_id)` | `.collection_id` `.registry_id` `.registry_title` `.markdown` `.entries` `.unresolved` `.contexts` `.general` `.ambiguous` `.truncated` `.contexts_truncated` `.reason` `.context_match` `.scan_truncated`; `RegistryEntry`: `.node_id` `.title` `.description` `.keywords` `.context` |
| `SkillReference` / `MarkdownSection` / `RegistryContext` / `RegistryGeneral` / `ContextLayout` | `parse_blocks(text)` / `parse_sections(text)` / `layout_contexts(text, blocks)` | `.kind` `.title` `.url` `.node_id` `.offset` / `.level` `.title` `.heading_start` `.body_start` `.end` / `.title` `.level` `.path` `.instruction` `.skills` `.range` / `.instruction` `.skills` / `.contexts` `.general` `.paths` `.truncated` |
| `Relations` | `repo.relations` | `.of()` `.create()` `.delete()` `.approve()`; `Relation`: `.type` `.from_id` `.to_id` `.from_title` `.to_title` `.ai_generated` `.approved` `.created_by` `.created_at` `.opposite_of()`; `RELATION_TYPES` lists the accepted kinds |

**What comes back from a search**

| You hold | From | On it |
|---|---|---|
| `SearchResult` | `repo.search(…)` (the flow returns the same as a `dict`) | `.hits` `.total` `.total_is_lower_bound` `.facets` `.suggestions` `.unresolved` `.ignored` `.warnings` `.raw` |
| `SearchHit` | `result.hits[i]` | `.id` `.title` `.url` `.description` `.source_url` `.mimetype` `.mediatype` `.preview_url` `.download_url` `.license` `.size` `.original_id` `.properties()` `.labels()` |
| `Facet` | `result.facets` | `.property` `.values` `.other_count` `.truncated`; `FacetValue`: `.value` `.count` |
| `UnresolvedFilter` | `result.unresolved` | `.field` `.value` `.suggestions` |

**The instance, and curated pages**

| You hold | From | On it |
|---|---|---|
| `Identity` | `repo.whoami()` | `.authority` `.username` `.display_name` `.is_anonymous` `.home_folder` `.raw` |
| `About` | `repo.about()` | `.repository_version` `.renderservice_version` `.api_version` `.services` `.plugins` `.features` `.themes_url` `.raw` |
| `MetadataSet` | `repo.metadatasets()` | `.id` `.name` |
| `CuratedPage` | `node.page.get()` | `.collection_id` `.folder_id` `.variants` `.rendered_id` `.total_variants` `.truncated` `.document` `.rendered` `.by_position` `.variant()` |
| `PageVariant` | `page.variant(…)`, `variant_from_node(…)` | `.id` `.title` `.is_template` `.target_group` `.educational_contexts` `.intention` `.education_levels` `.swimlanes` `.readable` `.node_ids` |
| `Swimlane` / `SwimlaneItem` | `variant.swimlanes` | `.heading` `.type` `.items` / `.widget` `.node_id` |
| `Ancestry` | `ancestry_of(…)`, `collections_of(…)` | `.node` `.parents` `.scope` |

**The neighbouring services, as objects**

| You hold | From | On it |
|---|---|---|
| `BildungsAPI` | `BildungsAPI(key, base_url=url)` or `.from_env()` | `.chat()` `.respond()` `.models()` `.load()` `.embeddings()` `.moderate()` `.images()` `.call()` `.aclose()` |
| `Answer` | `.chat()` / `.respond()` | `.text` `.status` `.reason` `.model` `.truncated` `.raw` |
| `Model` | `.models()` | `.id` `.name` `.demand` `.status` `.input` `.output` `.owned_by` `.shutdown_date` `.is_ready` `.can_chat` `.is_retired_on()` |
| `LoadReport` | `.load()` | `.provider` `.models` `.reports_load` `.retired` `.total` `.least_loaded` `.summary()`; free functions `load_report()` `rank_models()` `rank_among()` `pick_model()` `is_rankable()` |
| `Moderation` / `GeneratedImage` | `.moderate()` / `.images()` | `.flagged` `.categories` `.scores` / `.url` `.b64` `.revised_prompt` |
| `BapiTemplates` | `BapiTemplates(key, base_url=url, metadataset=…)` or `.from_env()` — needs no `BildungsAPI` | `.chat()` `.chat_limited()` `.respond()` `.respond_limited()` `.images()` `.images_limited()` `.suggest()` `.qas()` `.aclose()`; `NodeConfig`: `.node_id` `.config_name`; the types `Config` and `Values`; `DEFAULT_USER` |
| `TextExtraction` | `TextExtraction(url)` or `.from_env()` | `.text_of()` `.ping()` `.aclose()`; `ExtractedText`: `.url` `.text` `.lang` `.status` `.char_count` `.truncated` `.reason` `.detail` |
| `MetadataAgent` | `MetadataAgent(url)` or `.from_env()` | `.schemas()` `.schema()` `.content_types()` `.content_type_for()` `.clear_cache()` `.aclose()`; `SchemaInfo`: `.file` `.profile_id` `.groups` `.field_count`; `ContentType`: `.uri` `.schema_file` `.label` `.icon` |
| `Transport` | `repo.raw` | `.request()` `.json()` `.is_repository_url()` `.aclose()` — for routes this library does not wrap |

**Free functions worth knowing**

| The job | The call |
|---|---|
| turn a title into a legal `cm:name` | `name_from_title(title)` |
| turn short names into properties, labels resolved | `resolve_vocabulary(repo, aliases, every_value=…)` → `(properties, unresolved)`; `every_value=True` for a read filter |
| judge a filter on a record locally | `carries(props, prop, values)` |
| walk a collection tree with the records | `walk_collections(repo, collection_id, depth=…, max_collections=…)` → `(entries, opened, truncated)` |
| pages among collection hits already fetched | `pages_among(found, text)` |
| read a skill document without I/O | `parse_blocks(text)` / `parse_sections(text)` / `layout_contexts(text, blocks)` |
| a collection's registry, outside the accessor | `load_registry(repo, collection_id)` |
| widen a weak query | `expand_query(query)` → `QueryVariant`: `.label` `.weight` `.text` |
| score a hit against a query yourself | `score_hit(hit, query, aliases)` / `query_terms(query)` / `term_matches(…)` |
| fold duplicates | `deduplicate(hits)` |
| a result as plain JSON | `result_as_dict(result)` / `hit_as_dict(hit)` |
| the stopword and synonym lists | `LanguageProfile`: `.stopwords` `.framing` `.synonyms`; `GERMAN_SYNONYMS` |
| normalise an instance URL | `normalize_repository_url(raw)` / `rest_base(repository_url)` / `path_segment(value)` / `is_unroutable_host(host)` |
| judge whether an address may be fetched | `unsafe_url_reason(url)` — `None` means it may; anything else is the refusal, ready to log |
| judge only its spelling (you resolve the host yourself) | `unsafe_url_syntax(url)` — backslash or embedded credentials, the two ways parsers disagree |
| a search that reranks and reports both halves | `search_reranked(repo, text)` |
| every sub-collection of one collection | `sub_collections(repo, id)` |
| a node's rating, from a node you hold | `rating_of(node)` / `rate(…)` / `unrate(…)` |
| cap text before it reaches a model | `cap_text(text, max_chars)` |

**Errors** — all inherit `EduSharingError`, so a single `except EduSharingError`
catches everything this library raises:

`TransportError` · `AuthenticationError` · `PermissionDeniedError` ·
`NotFoundError` · `ValidationError` · `ConflictError` · `SilentDropError` ·
`ServerError` · `UnsafeUrlError` · `ContentTooLargeError` (a download above
`max_bytes`; the text paths stop at `MAX_TEXT_BYTES`, 8 MiB, before downloading) ·
`RateLimitedError` (429 — `retry_after` carries the seconds the server named;
short waits are sat out for you, a long one reaches you with the number)

**Retries** are one rule for all three clients: `RetryPolicy(max_retries=…,
backoff_base=…, max_retry_after=…)`, whose `delay(attempt, retry_after=…)`
returns the seconds to wait — jittered, so a fan-out does not come back in
lockstep — or `None` when the server asked for longer than this client waits.
`RETRYABLE_STATUS` is the status set the two sibling services retry,
`DEFAULT_MAX_RETRY_AFTER` (60 s) is that ceiling, and
`parse_retry_after(value)` reads the header in either form RFC 9110 allows.
A refused 3xx names only the target host -- a presigned address carries its
authority in the query string -- and puts the whole `Location` on the
exception as `.location`.

`edusharing.dto` is the one reading of a raw node record — `first(value)`
(the first value of a property, `None` for an empty list), `title_of(raw)`
(`title`, then `cclom:title`, `cm:title`, `cm:name`) and `stored_title_of(raw)`
(the same without the name fallback — what a write preserves), `node_id_of(raw)`,
`bare_id(ref)`, `render_url(repository_url, node_id)` and
`page_total(response, default=…)`. Every object of this library is built
through them, so the same record always reads the same way.

`page_cut(records, response, limit)` is the one reading of *"is this page all
of them?"*. Ask the endpoint for `limit + 1` and the page answers for itself;
reading the stated total alone said "complete" exactly where the repository
stated nothing, which is where the question mattered most.

`at_least(name, value, limit)` is the bounds check for the clients' **continuous**
settings and `whole_number(name, value, limit)` the one for those that **count**
(`max_concurrency`, `max_retries`, `retries_before_switching`) -- a fraction is
refused there, because a semaphore counting 1.5 never reaches the zero at which
it would block;
`check_client(client, timeout=…)` holds the three rules for a client the caller brings
along -- no `timeout` beside it, no `follow_redirects=True`, because httpx keeps
custom headers across a cross-origin redirect and an API key would travel with them,
no credentials of the client's own (`auth=` or a default header beyond httpx's
four), because those go to every address including one outside the repository,
and no cookies already in its jar, because switching the jar off does not empty
it and httpx copies what is in there onto every request;
`redirect_error(…)` and `non_json_error(…)` are the two answers all four clients
give to a 3xx and to a body that is not JSON -- both inside `EduSharingError`, so
nothing from the standard library escapes the contract;
`details_withheld(…)` names what an error deliberately does not reveal.

**The rest of `__all__`** is machinery you only touch when extending the
library rather than using it: `Flows` (the type behind `repo.flows`), `__version__`,
the constructors `from_response` / `from_node` / `from_raw_header` / `error_from_response`
(and `error_class_for`, which answers only which type a status stands for), the b-api body helpers `build_body` / `read_answer` /
`reasoning_for_responses`, and `field_property`, which maps a short field name to
its property. Nothing above depends on calling them.

**Named constants — the defaults, and the magic strings**

Every default below is a keyword argument you can override; the constant exists
so the value has a name instead of being buried in a signature.

| Constant | Value | What it governs |
|---|---|---|
| `DEFAULT_EFFORT` / `DEFAULT_VERBOSITY` | `"low"` | reasoning and verbosity on models that support them |
| `DEFAULT_MAX_TOKENS` / `DEFAULT_MAX_OUTPUT_TOKENS` | `1000` | the cap on a chat answer / on a responses answer |
| `DEFAULT_HIT_CHARS` / `DEFAULT_RESULT_CHARS` | `400` / `4000` | how much `format_hit` / `format_results` hands a model |
| `DEFAULT_MAX_CHARS` | `200000` | where `flows.text` cuts, at a word boundary |
| `SKILL_SEARCH_PAGE` / `SKILL_BUNDLE_MAX` / `SKILL_VISIT_MAX` / `SKILL_DEPTH_MAX` | `50` / `50` / `30` / `2` | skill hits pooled · companion files listed before a folder counts as an inbox · collections a scoped walk may read · levels the walk descends |
| `REGISTRY_SCAN_MAX` / `REGISTRY_MAX` / `REGISTRY_POOL` / `REGISTRY_CONTEXT_MAX` | `50` / `100` / `10` / `50` | files scanned for a registry · entries per answer · heads resolved at once · contexts per answer |
| `DUPLICATE_SCAN_LIMIT` | `20` | hits `find_by_url` compares before `add_material` creates; `check_before_create` applies `if_exists`, `validate_if_exists` refuses a misspelled one |
| `EXCLUSION_MAX` | `200` | the largest refill after `exclude_ids` — `limit` itself is never capped |
| `DEFAULT_POOL` | `25` | how many hits `search(rerank=True)` fetches before reranking |
| `MAX_VARIANTS` | `5` | how many rewrites `expand_query` produces |
| `DEFAULT_MAX_COLLECTIONS` / `DEFAULT_MAX_WIDGETS` / `DESCRIBE_MANY_MAX` | `50` / `24` / `50` | ceilings on `browse_tree`, on a rendered page, and on the distinct ids one `describe_many` looks at (it answers `truncated`) |
| `RELATED_ON` | `("subject", "level")` | the fields `related()` compares on by default |
| `METHODS` | `("simple", "browser")` | the extraction methods `text_of` accepts |
| `PROPOSAL_BATCH` | `"edusharing-python"` | the batch name proposals are filed under |
| `GERMAN` | a `LanguageProfile` | the German stopword, framing and synonym lists |

| Constant | Value | Why it has a name |
|---|---|---|
| `KEYWORD_PROPERTY` | `cclom:general_keyword` | the shared keyword list (see [TRAPS.md 1.6](reference/TRAPS.md#16-some-lists-are-shared-property)) |
| `CHILD_ASPECT` / `ORDER_PROPERTY` / `LIST_MAX` | `ccm:io_childobject` / `ccm:childobject_order` / `200` | what marks and orders a child object, and how many one listing reads before it raises |
| `PAGE_REF` / `PAGE_CONFIG` / `VARIANT_CONFIG` | `ccm:page_config_ref` / `ccm:page_config` / `ccm:page_variant_config` | the three properties a curated page hangs on |
| `EVERYONE` / `CONSUMER` | `GROUP_EVERYONE` / `Consumer` | the authority and right that make a node public |
| `GUEST_AUTHORITY` | `esguest` | who you are when nobody signed in |
| `UNTRUSTED_MARKER` | the fence `as_untrusted` wraps text in | so a model can see where foreign text begins |

`UNSET` is the sentinel behind the rule **a default may be dropped, an explicit
wish may not**: passing nothing lets the library omit a parameter a model does
not support; passing a value explicitly makes an unsupported parameter an
error rather than a silent omission. `ReasoningParam` is its type.

---

## 4. How edu-sharing stores metadata

Moved to [reference/TRAPS.md, part 1](reference/TRAPS.md#1-how-edu-sharing-stores-metadata):
every value is a list, four namespaces, `cm:name` is a key, vocabulary fields
hold URIs, the metadata set decides what exists, shared lists, aspects, and
properties that arrive empty.

---

## 5. The traps — what to watch for

Moved to [reference/TRAPS.md, part 2](reference/TRAPS.md#2-the-traps--what-to-watch-for):
sixteen traps, each measured against a real instance — from "HTTP 200 does
not mean it was stored" to the template mode. The one to know before reading
any result: `total_is_lower_bound`, `truncated`, `complete`,
`collections_truncated`, `scan_truncated` and `contexts_truncated` each say
that something is missing (part 2.3).

---

## 6. Putting it behind a model

### Never let repository text act as an instruction

Descriptions, titles and comments are written by strangers. Wrap them before
they enter a model context:

```python
from edusharing.agent import as_untrusted, sanitize_text

as_untrusted(hit.description, label="description")
```

### Input you do not trust belongs in `choices`, not `variables`

In the template mode a `variables` value goes into the prompt as it stands —
measured, one reading "ignore all previous instructions" steered the answer.
The `_limited` calls take `{widget_id: value_id}` pairs instead; free text given
there did not reach the prompt.

### Propose, do not write

For anything a model decided, the route is `suggestions.propose(...)` and a
person decides — not `node.update(...)`. The b-api's template mode proposes
the same way: `BapiTemplates.suggest` stores pending suggestions, and
`repo.flows.accept_suggestion` takes one over (measured 2026-09-11). When a
write really is intended, plan it and show the plan:

```python
# async: plan_update and apply() are coroutines
plan = await plan_update(node, title=proposed)
print(plan.describe())        # old -> new, for a human
await plan.apply()            # only after confirmation
```

### One shape for success and failure

```python
# async: as_result takes an awaitable
outcome = await as_result(repo.flows.search(text))
outcome.ok, outcome.error_type      # False, "NotFoundError"
```

`error_type` lets a tool distinguish "rephrasing might help" from "credentials
are missing" without parsing the message. Errors carry no Java stack trace.

### Addresses from a model are untrusted

`check_url` refuses loopback, link-local and private ranges. `BildungsAPI.call`
validates its route segment by segment — `"../../administration/account"` is
refused rather than sent with the API key.

### What never reaches a log

Headers, credentials, query strings, and the path of any address the caller
supplied. The library logs only what it built itself.

---

## 7. Where to look things up

| Question | File |
|---|---|
| what does this call return, exactly | [`docs/REFERENCE.md`](../../../docs/REFERENCE.md) · [de](../../../docs/REFERENCE.de.md) |
| why does this flow do what it does | [`docs/FLOWS.md`](../../../docs/FLOWS.md) · [de](../../../docs/FLOWS.de.md) |
| how is the library built | [`docs/ARCHITECTURE.md`](../../../docs/ARCHITECTURE.md) · [de](../../../docs/ARCHITECTURE.de.md) |
| a runnable example | `docs/examples/01…23` — see the README table |
| what changed | `CHANGELOG.md` |

Start with `docs/examples/10_two_levels.py` when deciding which level to write
against: it writes the same use case twice and counts the requests each sends.

---

## 8. Checklist before shipping a tool built on this

```
[ ] Instance comes from configuration, not from a literal in the code
[ ] Credentials from env or a vault, never in source, never logged
[ ] Every search result: `unresolved` checked and surfaced
[ ] Every count reported: `total_is_lower_bound` respected
[ ] Every walk: `truncated` / `complete` surfaced
[ ] Every write: SilentDropError handled, not swallowed
[ ] Repository text wrapped with `as_untrusted` before a model sees it
[ ] URLs from a model passed through `check_url`
[ ] Model-decided changes go through `suggestions.propose`, not `update`
[ ] Errors caught as `EduSharingError`, reported with `error_type`
```

---

## 9. Related skills

| Skill | For |
|---|---|
| `wlo-edu-sharing-api` | the raw REST API, WLO's data model, licence keys, NGSearch |
| `wlo-environments` | which address is staging, which is production; variable names |
| `wlo-metadata-agent-api` | the metadata agent's own endpoints |
| `wlo-bapi-llm` / `wlo-b-api-llm` | the gateway's model list and provider behaviour |
| `wlo-suggestions-curation` | the editorial workflow this library's `suggestions` feeds |
| `wlo-mcp-search` / `wlo-mcp-python-client` | building an MCP server over this |

When those skills and this one disagree about a *Python* call, this one and
`docs/REFERENCE.md` win. When they disagree about an *address*, a *raw
endpoint* or WLO's data model, they win.
