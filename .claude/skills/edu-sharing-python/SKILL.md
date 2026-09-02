---
name: edu-sharing-python
description: Using the edu-sharing-python-client library (import `edusharing`) — both levels (API objects and flow dicts), all 20 flows, the complete public surface object by object, how edu-sharing stores metadata (list-valued properties, the cm:/cclom:/ccm:/virtual: namespaces, cm:name versus cclom:title, vocabulary URIs, metadata sets), the neighbouring services (b-api LLM gateway, text extraction, metadata agent), the measured traps, and the rules for putting it behind a model. Use when writing Python against an edu-sharing repository, building an MCP server or agent tool over WLO/OpenEduHub content, or when a call returned HTTP 200 and stored nothing. Trigger u.a. "edu-sharing Python", "edusharing library", "repo.flows", "SilentDropError", "Bibliothek nutzen", "Suche in Python", "Material anlegen Python", "MCP-Werkzeug edu-sharing", "b-api Python", "Textextraktion", "metadata agent schema", "welcher Aufruf für", "unresolved", "total_is_lower_bound", "cm:name", "cclom:title", "propertyFilter", "Metadatensatz", "properties leer", "Eigenschaft schreiben".
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
```

The three neighbouring services each take **their own** address and also have
no default — `from_env()` refuses without the variable rather than sending data
to a host nobody chose:

| Service | Class | Variable |
|---|---|---|
| LLM gateway (b-api) | `BildungsAPI` | `B_API_BASE_URL` + `B_API_KEY` |
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
| every value of a field, or a substring of one | `repo.vocab.values(prop)` / `repo.vocab.suggest(prop, "ysik")` |
| a label's filter value — **all** of them | `repo.vocab.resolve_all(prop, "Biologie")` |
| a poorly phrased query ("something about fractions") | `repo.flows.search(text, rerank=True)` |
| search *inside* one collection | `repo.flows.search_in_collection(id, text)` |
| find collections that render a curated page | `repo.flows.find_pages(text)` |

### Reading one thing

| The task | The call |
|---|---|
| everything about a node, as JSON | `repo.flows.describe(node_id)` |
| several nodes at once | `repo.flows.describe_many(ids)` |
| where does it sit (breadcrumb) | `repo.flows.placement(node_id)` |
| what is in this collection | `repo.flows.collection_contents(id)` |
| what hangs *under* this material | `repo.flows.child_objects(node_id)` |
| what stands *beside* it | `repo.flows.relations(node_id)` |
| what is underneath, recursively | `repo.flows.browse_tree(id, depth=2)` |
| how much is in there | `repo.flows.collection_stats(id)` |
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
| build a collection and fill it | `repo.flows.build_collection(title, node_ids)` |
| put existing material into a collection | `repo.add_to_collection(collection_id, node_id)` |
| the collection accessor behind those shortcuts | `repo.collections.find/create/update/add/remove` |
| take it out again (material stays) | `repo.remove_from_collection(collection_id, node_id)` |
| delete | `repo.flows.delete(node_id)` |
| upload a file | `node.content.upload(data, filename=…, mimetype=…)` |
| attach an answer sheet | `node.children.add(data, filename=…, mimetype=…)` |
| link two materials | `repo.relations.create(a, "isPartOf", b)` |
| make it publicly readable | `node.permissions.publish()` |
| keywords | `node.add_keywords([...])` / `node.remove_keywords([...])` |

### Editorial surfaces (no flow — API level only)

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

The tables above route the twenty common jobs. Everything else is reached
through an object you already hold. This names every public member, so nothing
has to be guessed — argument and return shapes are in `docs/REFERENCE.md`.

**Getting in**

| You hold | From | On it |
|---|---|---|
| `Repository` | `Repository(url, credential=…)` or `.from_env()` | `.search()` `.node()` `.create_node()` `.children()` `.create_collection()` `.update_collection()` `.add_to_collection()` `.remove_from_collection()` `.find_collections()` `.resolve()` `.resolve_all()` `.about()` `.whoami()` `.metadatasets()` `.close()`; `.url` `.credential` `.metadataset` `.raw` `.flows` `.people` `.relations` |
| `AsyncRepository` | the same, inside an event loop | the same names awaited, `.aclose()` for `.close()`, plus `.nodes` `.collections` `.vocab` `.searcher` |
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
| `Collections` | `repo.collections` — **async only** | `.find()` `.create()` `.update()` `.add()` `.remove()` |
| `Nodes` | `repo.nodes` — **async only** | `.get()` `.create()` `.children()` `.repository_url`; `ChildPage`: `.nodes` `.total` `.offset` |
| `Search` | `repo.searcher` — **async only** | `.search()` |
| `Vocabulary` | `repo.vocab` — **async only** | `.values()` `.suggest()` `.resolve()` `.resolve_all()` `.clear_cache()`; `VocabularyValue`: `.uri` `.label` |
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
| `CuratedPage` | `node.page.get()` | `.collection_id` `.folder_id` `.variants` `.rendered_id` `.document` `.rendered` `.by_position` `.variant()` |
| `PageVariant` | `page.variant(…)`, `variant_from_node(…)` | `.id` `.title` `.is_template` `.target_group` `.educational_contexts` `.intention` `.education_levels` `.swimlanes` `.readable` `.node_ids` |
| `Swimlane` / `SwimlaneItem` | `variant.swimlanes` | `.heading` `.type` `.items` / `.widget` `.node_id` |
| `Ancestry` | `ancestry_of(…)`, `collections_of(…)` | `.node` `.parents` `.scope` |

**The neighbouring services, as objects**

| You hold | From | On it |
|---|---|---|
| `BildungsAPI` | `BildungsAPI(url, key)` or `.from_env()` | `.chat()` `.respond()` `.models()` `.load()` `.embeddings()` `.moderate()` `.images()` `.call()` `.aclose()` |
| `Answer` | `.chat()` / `.respond()` | `.text` `.status` `.reason` `.model` `.truncated` `.raw` |
| `Model` | `.models()` | `.id` `.name` `.demand` `.status` `.input` `.output` `.owned_by` `.shutdown_date` `.is_ready` `.can_chat` `.is_retired_on()` |
| `LoadReport` | `.load()` | `.provider` `.models` `.reports_load` `.retired` `.total` `.least_loaded` `.summary()`; free functions `load_report()` `rank_models()` `rank_among()` `pick_model()` `is_rankable()` |
| `Moderation` / `GeneratedImage` | `.moderate()` / `.images()` | `.flagged` `.categories` `.scores` / `.url` `.b64` `.revised_prompt` |
| `TextExtraction` | `TextExtraction(url)` or `.from_env()` | `.text_of()` `.ping()` `.aclose()`; `ExtractedText`: `.url` `.text` `.lang` `.status` `.char_count` `.truncated` `.reason` `.detail` |
| `MetadataAgent` | `MetadataAgent(url)` or `.from_env()` | `.schemas()` `.schema()` `.content_types()` `.content_type_for()` `.clear_cache()` `.aclose()`; `SchemaInfo`: `.file` `.profile_id` `.groups` `.field_count`; `ContentType`: `.uri` `.schema_file` `.label` `.icon` |
| `Transport` | `repo.raw` | `.request()` `.json()` `.is_repository_url()` `.aclose()` — for routes this library does not wrap |

**Free functions worth knowing**

| The job | The call |
|---|---|
| turn a title into a legal `cm:name` | `name_from_title(title)` |
| turn short names into properties, labels resolved | `resolve_vocabulary(repo, aliases)` → `(properties, unresolved)` |
| read a skill document without I/O | `parse_blocks(text)` / `parse_sections(text)` / `layout_contexts(text, blocks)` |
| a collection's registry, outside the accessor | `load_registry(repo, collection_id)` |
| widen a weak query | `expand_query(query)` → `QueryVariant`: `.label` `.weight` `.text` |
| score a hit against a query yourself | `score_hit(hit, query, aliases)` / `query_terms(query)` / `term_matches(…)` |
| fold duplicates | `deduplicate(hits)` |
| a result as plain JSON | `result_as_dict(result)` / `hit_as_dict(hit)` |
| the stopword and synonym lists | `LanguageProfile`: `.stopwords` `.framing` `.synonyms`; `GERMAN_SYNONYMS` |
| normalise an instance URL | `normalize_repository_url(raw)` / `rest_base(repository_url)` / `path_segment(value)` / `is_unroutable_host(host)` |
| a search that reranks and reports both halves | `search_reranked(repo, text)` |
| every sub-collection of one collection | `sub_collections(repo, id)` |
| a node's rating, from a node you hold | `rating_of(node)` / `rate(…)` / `unrate(…)` |
| cap text before it reaches a model | `cap_text(text, max_chars)` |

**Errors** — all inherit `EduSharingError`, so a single `except EduSharingError`
catches everything this library raises:

`TransportError` · `AuthenticationError` · `PermissionDeniedError` ·
`NotFoundError` · `ValidationError` · `ConflictError` · `SilentDropError` ·
`ServerError` · `UnsafeUrlError`

`at_least(name, value, limit)` is the bounds check the clients apply to their settings;
`details_withheld(…)` names what an error deliberately does not reveal.

**The rest of `__all__`** is machinery you only touch when extending the
library rather than using it: `Flows` (the type behind `repo.flows`), `__version__`,
the constructors `from_response` / `from_node` / `from_raw_header` / `error_from_response`, the b-api body helpers `build_body` / `read_answer` /
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
| `SKILL_SEARCH_PAGE` / `SKILL_BUNDLE_MAX` / `SKILL_VISIT_MAX` | `50` / `50` / `30` | skill hits pooled · companion files listed before a folder counts as an inbox · collections a scoped walk may read |
| `REGISTRY_SCAN_MAX` / `REGISTRY_MAX` / `REGISTRY_POOL` / `REGISTRY_CONTEXT_MAX` | `50` / `100` / `10` / `50` | files scanned for a registry · entries per answer · heads resolved at once · contexts per answer |
| `DUPLICATE_SCAN_LIMIT` | `20` | hits `find_by_url` compares before `add_material` creates; `check_before_create` applies `if_exists` |
| `EXCLUSION_MAX` | `200` | the largest page `search` refills to after `exclude_ids` |
| `DEFAULT_POOL` | `25` | how many hits `search(rerank=True)` fetches before reranking |
| `MAX_VARIANTS` | `5` | how many rewrites `expand_query` produces |
| `DEFAULT_MAX_COLLECTIONS` / `DEFAULT_MAX_WIDGETS` | `50` / `24` | ceilings on `browse_tree` and on a rendered page |
| `RELATED_ON` | `("subject", "level")` | the fields `related()` compares on by default |
| `METHODS` | `("simple", "browser")` | the extraction methods `text_of` accepts |
| `PROPOSAL_BATCH` | `"edusharing-python"` | the batch name proposals are filed under |
| `GERMAN` | a `LanguageProfile` | the German stopword, framing and synonym lists |

| Constant | Value | Why it has a name |
|---|---|---|
| `KEYWORD_PROPERTY` | `cclom:general_keyword` | the shared keyword list (see 4.6) |
| `CHILD_ASPECT` / `ORDER_PROPERTY` | `ccm:io_childobject` / `ccm:childobject_order` | what marks and orders a child object |
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

Knowing the calls is not enough to write correct code against a repository.
These eight properties of the underlying store explain most of what would
otherwise look like the library behaving strangely.

### 4.1 Every value is a list

A property is never a scalar. `node.properties` is `dict[str, list[str]]` — a
title is a one-element list, a subject with three values is a three-element
list, and an absent property is a missing key, not an empty string.

```python
node.properties["cclom:title"]      # ["Fractions explained"] -- a list
node.get("cclom:title")             # "Fractions explained"   -- the first value
node.get_all("ccm:taxonid")         # every value, [] if unset
```

Use `get()` when you want one, `get_all()` when the field may legitimately
carry several. Reaching into `properties` directly and treating the result as a
string is the single most common mistake.

### 4.2 Four namespaces, and they mean different things

| Prefix | Comes from | Example |
|---|---|---|
| `cm:` | Alfresco's own content model — the file system underneath | `cm:name`, `cm:title`, `cm:description` |
| `cclom:` | the learning-object metadata standard | `cclom:title`, `cclom:general_keyword`, `cclom:general_description` |
| `ccm:` | edu-sharing's own additions | `ccm:taxonid`, `ccm:educationalcontext`, `ccm:wwwurl` |
| `virtual:` | not part of the stored model — a service puts them on the response | `virtual:profiling_widget_intention` |

Two consequences. A property you invent under `ccm:` will not exist for the
metadata set (see 4.5). And a `virtual:` value you read back is owned by
whichever service produced it — on curated pages that is the page builder — so
treat it as something to read, and change it through the tool that owns it.

### 4.3 `cm:name` is a key, not a title

`cm:name` is the node's name **inside its parent folder** — the equivalent of a
filename. It must be unique among its siblings, and the repository rejects or
mangles characters a filename cannot carry. The human-readable title is a
different field.

```python
name_from_title("Bruchrechnung: Übung 1/2")   # a legal cm:name
```

Worse, the title field is not the same everywhere: **material carries
`cclom:title`, a collection carries `cm:title`.** Writing the wrong one leaves
the object looking untitled. The library's `title=` shorthand writes both, so
prefer it over naming the property yourself.

### 4.4 Vocabulary fields hold URIs, never labels

`ccm:taxonid` does not contain `"Biologie"`; it contains a URI from a
SKOS vocabulary. Filtering or writing a label puts a value in that matches
nothing.

```python
await repo.vocab.resolve_all("subject", "Biologie")
# -> both URIs: the school subject and the university subject
```

One label can belong to two vocabularies — measured against staging, 25 subject
labels appear both under school subjects and under university subjects. This is
why `resolve_all` returns a list and the search filters on all of them; taking
only the first finds half the material.

### 4.5 The metadata set decides what exists — silently

Every instance carries one or more metadata sets (`repo.metadatasets()`) that
define which properties an object may hold. A property the set does not know is
**not** rejected: the repository answers `200 OK` and stores nothing.

This is why every write in this library reads back and raises `SilentDropError`
on a mismatch. Do not switch that off, and do not treat a `200` as proof.

### 4.6 Some lists are shared property

`cclom:general_keyword` is maintained jointly — by editors, by crawlers, by
other applications. Setting it replaces everyone else's work.

```python
await node.add_keywords("fractions")        # merges
await node.update(keywords=["fractions"])   # replaces -- rarely what you want
```

The same care applies to any list-valued field you did not author alone.

### 4.7 Aspects are not types

A node has one type (`ccm:io` for material, `ccm:map` for a collection) and any
number of aspects layered on top. A child object is not a type of node — it is a
normal node carrying the aspect `ccm:io_childobject`. Searching for it as a type
finds nothing.

### 4.8 Properties arrive empty unless you ask for them

Several repository routes return nodes with an empty `properties` map unless the
request carries `propertyFilter=-all-`. The library sets it where it calls those
routes; if you go around the library with `repo.raw.request(...)`, you have to
set it yourself, or you will conclude the data is missing when it is merely
unrequested.

---

## 5. The traps — what to watch for

Each of these was measured against a real instance. They are the reason the
library exists.

### 5.1 HTTP 200 does not mean it was stored

edu-sharing accepts writes it then discards. Every write in this library reads
back and raises `SilentDropError` instead of reporting success.

```python
try:
    await node.update(title="Neu")
except SilentDropError as exc:
    exc.dropped        # {"cclom:title": ["Neu"]}
```

**If you write through `repo.raw`, you lose this.** Read back yourself.

Known droppers: `relations.create(metadata=...)` (accepted, stored nowhere),
and metadata-set fields the instance does not know.

### 5.2 `unresolved` is not decoration

A filter value the instance does not know is **not applied**, and the search
answers a wider question than you asked.

```python
answer = await repo.flows.search("Zellen", subject="Bio")
answer["unresolved"]   # [{"field": "subject", "value": "Bio",
                       #   "suggestions": ["Biologie"]}]
```

Same for writing: `add_material` and `update_material` return `unresolved` for
values that were **not** written. The material exists without them.

**Never report a result to a user or a model without checking this.**

### 5.3 `total_is_lower_bound`, `truncated`, `complete`

- `total_is_lower_bound=True` → `total` counts *at least* that many. Reporting
  it as an exact figure states a number that is not one.
- `browse_tree`/`search_in_collection`: `truncated=True` → the walk stopped
  early. An empty result then does **not** mean "there is none".
- `collection_stats`: `complete=False` → the breakdown is a sample.

`find_collections` always sets `total_is_lower_bound`: it merges two routes.

### 5.4 A collection is not a folder, and a search cannot be scoped to it

- Create collections through `repo.create_collection`, never as a `ccm:map`
  node. A node created the other way is not a collection to the rest of the
  system.
- Collections form a **graph**, not a tree — a collection can have several
  parents. `browse_tree` guards against cycles and says so via `truncated`.
- There is no search scoped to a collection. `virtual:primaryparent_nodeid`
  returns HTTP 400, and it would be the wrong answer anyway: a curated
  collection holds *references* to nodes whose primary parent lives elsewhere.
  `search_in_collection` walks and filters locally.
- `collection_contents` asks **two** routes. Material alone reports a
  collection of sub-collections as empty.

### 5.5 Three different kinds of belonging

| | Holds | Read with |
|---|---|---|
| Collection | references to material that also lives elsewhere | `collection_contents` |
| Child object | a document *under* one material, no life of its own | `child_objects` |
| Relation | two materials standing *side by side* | `relations` |

A child object carries its filename in `name` and an **empty** `title`. Every
other flow displays `title`, so reaching for it here shows nothing.

Relations keep the opposite direction automatically: create `isPartOf` from the
episode and the series reports `hasPart`. A fresh relation is
`approved=False` — `relations.approve(...)` sets it.

### 5.6 Labels versus URIs

`node.get("ccm:taxonid")` gives the URI. `node.labels("ccm:taxonid")` gives
"Mathematik". `SearchHit.labels` does the same. The flow level resolves labels
for you in `fields`.

Facet *values* are URIs and carry no label — `FacetValue` has `value` and
`count` only.

Which short names (`subject`, `level`, …) exist is **read from the instance**,
not fixed in the library: `repo.searcher.field_aliases`.

**One label can belong to two vocabularies.** Measured 2026-08-31 against
staging, 25 subject labels sit in both `discipline` (school subjects) and
`hochschulfaechersystematik` (university subjects) — `Biologie`, `Chemie`,
`Physik` among them. A search on the label filters on **all** of them, because
finding half the material while looking like all of it is a wrong answer:

```python
await repo.vocab.resolve(prop, "Biologie")      # the first — one of two
await repo.vocab.resolve_all(prop, "Biologie")  # both, which is what search uses
```

Writing takes the first, deliberately: tagging a year 6 worksheet as a
university subject is a claim, not a widening. Add a `level` filter to keep the
halves apart.

### 5.7 Paging, limits and defaults that truncate

- `repo.people.members(group)` defaults to 10 and truncates silently. Pass
  `limit`.
- `collection_contents` needs `propertyFilter=-all-` to get properties at all;
  the library sets it. Through `repo.raw` you must set it yourself.
- The extraction service's two methods are **not** ranked: measured, `simple`
  returned an article where `browser` returned a cookie banner. If one yields
  nothing, try the other.

### 5.8 A framing word ruins a query

Measured over a 60-node pool: `"Bruchrechnung"` matched 0 nodes and
`"die Bruchrechnung"` matched 43. `rerank=True` expands and re-scores the
query; it costs several requests, so use it when the query comes from a human
or a model, not for a machine-built filter query.

`rerank=True` and `offset` do not combine — the pool is merged across variants,
so an offset into it would not mean what a caller expects.

### 5.9 Dead index entries

Measured: 4 of 25 search hits were no longer retrievable. `describe_many`
reports them in `failed` instead of raising, so a shorter list than requested
is distinguishable from "these do not exist".

### 5.10 The two providers are not interchangeable

Measured 2026-08-31. `openai` offers 132 models and reports no load;
`academiccloud` offers 15 and reports `demand` 0 to 23, which moves by the
minute. Both carry `chat/completions` and `responses`. Only OpenAI carries
`embeddings`, `moderations` and `images/generations` — the AcademicCloud
answers 404 and its models produce `text` and `thought`, nothing else.

`reasoning_effort` and `verbosity` work on the gpt-5 and o series and are
refused by older OpenAI models with 400. The AcademicCloud accepts them and
ignores them: identical token usage at `low` and `high`. Its lever is
`chat_template_kwargs`, which the library sets for Qwen3.

The library defaults both to `low` and applies them only where they work.
**An explicit value is never dropped for you** — it raises instead, because an
answer produced without the effort you asked for looks exactly like one
produced with it.

A virtual model (`model=["a","b","c"]`, or a name from `virtual_models`) takes
the least loaded of them. That is worth having at the AcademicCloud; at OpenAI
it degenerates into a fallback chain in the order you wrote.

### 5.11 Asking for load, and switching instead of waiting

`demand` moves by the minute, so the model list is cached 30 seconds. Match
that to how long your process lives:

```python
# A script that runs for a minute: ask once.
api = BildungsAPI.from_env(models_cache_seconds=CACHE_FOREVER)
print((await api.load()).summary())      # into the start-up log

# A service that runs for a day: leave the 30 seconds alone. CACHE_FOREVER
# would have it choosing models on figures from hours ago.
```

`load()` returns a `LoadReport`. **Read `reports_load` first** — at OpenAI it
is `false`, no load is reported at all, and the ranking is alphabetical rather
than a statement about queues.

**Switching beats waiting while there is somewhere to switch to.** A 503 is
retryable, so a busy model used to consume the full `max_retries` — roughly
17 s at the default backoff — with another model standing right next to it.
A candidate now gets `retries_before_switching` retries (default 1) while
another remains; the last one keeps the full budget. `max_retries=0` still
means exactly one attempt each: the knob only lowers.

A 429 is the case this cannot help — the AcademicCloud limits the key, not the
model, so the next candidate fails just as fast.

### 5.12 On the blocking `Repository`, four accessors are still asynchronous

`Repository` wraps most of what it hands out so it blocks. Four properties do
not: `repo.vocab`, `repo.searcher`, `repo.collections` and `repo.nodes` return
the asynchronous objects unchanged. Calling a method on them from blocking code
produces a coroutine that is never awaited — no error, no effect.

```python
repo = Repository(url, credential=cred)
repo.collections.find("Bruchrechnung")   # a coroutine object -- does nothing
repo.find_collections("Bruchrechnung")   # the blocking route
```

Every one of them has a blocking counterpart on the repository itself:

| Instead of | Use |
|---|---|
| `repo.nodes.get/create/children` | `repo.node()` / `repo.create_node()` / `repo.children()` |
| `repo.collections.find/create/update/add/remove` | `repo.find_collections()` / `repo.create_collection()` / `repo.update_collection()` / `repo.add_to_collection()` / `repo.remove_from_collection()` |
| `repo.searcher.search` | `repo.search()` |
| `repo.vocab.resolve` / `.resolve_all` | `repo.resolve()` / `repo.resolve_all()` |
| `repo.vocab.values` | `repo.flows.vocabulary(field)` |

`repo.vocab.suggest` and `repo.vocab.clear_cache` have no blocking
counterpart; everything a caller needs for filtering does.

---

### 5.13 A collection listing hands out reference ids

A collection holds **references**, not records. `collection_contents`,
`search_in_collection` and every collection-scoped listing return the ids of
those references — the ordinary way to obtain an id, not an edge case. Measured
on staging (2026-09-02): `/usage` answers a reference id with an empty list and
the original with two collections; and a write aimed at a reference is stored
on the reference and never reaches the record (measured by the MCP,
2026-08-17) — the read-back cannot notice, because it re-reads the same node.

The library resolves this. `node.original_id` names the record (`None` on an
original), `node.collections()` and `flows.placement` ask for the original, and
`update()`, `set_property()` and `add_keywords()` write to it and return the
**original** with `redirected_from` set. Deleting is *not* redirected: deleting
a reference removes only the reference, which is harmless, and `flows.delete`
says `is_reference` so you know which of the two went.

```python
node = await repo.node(listing_id)
node.is_reference            # True
changed = await node.update(title="…")
changed.id                   # the original's id, not listing_id
changed.redirected_from      # listing_id -- the write was redirected
```

---

### 5.14 A skill is a record with a content type — and the metadata set decides whether you can filter on it

Skills are ordinary records whose content type says "instruction" and whose
attached file is the `SKILL.md`. Measured on staging (2026-09-02): with
`mds_oeh` the content type is a search criterion and 34 skills answer; with
`-default-` the repository refuses the criterion (`ValidationError`, and the
message says why). Set `EDU_SHARING_METADATASET=mds_oeh` or pass
`metadataset=` — `from_env()` reads the variable since 2026-09-02.

Two more measured traps: the `SKILL.md` is read with `download()`, because
`/textContent` is empty for Markdown; and a skill's folder (its companion
files) answered 403 anonymously — `files_reason` says so instead of showing
an empty list as "travels alone".

Everything that names a convention — the content-type URIs, how a registry
document gives itself away, the block kinds — is `SkillConventions`, a
parameter whose default is WLO's `WLO_SKILLS`. Another repository passes its
own. And the Markdown that comes back is uploaded content: frame it with
`as_untrusted` before it reaches a prompt.

```python
repo = AsyncRepository(url, metadataset="mds_oeh")
found = await repo.flows.find_skills("Fragen generieren")
doc = await repo.flows.skill(found["hits"][0]["id"])
doc["files_reason"]          # "folder_unreadable" anonymously
```

---

## 6. Putting it behind a model

### Never let repository text act as an instruction

Descriptions, titles and comments are written by strangers. Wrap them before
they enter a model context:

```python
from edusharing.agent import as_untrusted, sanitize_text

as_untrusted(hit.description, label="description")
```

### Propose, do not write

For anything a model decided, the route is `suggestions.propose(...)` and a
person decides — not `node.update(...)`. When a write really is intended, plan
it and show the plan:

```python
plan = await plan_update(node, title=proposed)
print(plan.describe())        # old -> new, for a human
await plan.apply()            # only after confirmation
```

### One shape for success and failure

```python
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
| a runnable example | `docs/examples/01…17` — see the README table |
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
