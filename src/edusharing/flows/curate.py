"""Writing flows: create, collect, delete.

Three things are done here that the API level leaves to the caller, and each of
them is a step people forget rather than a step they enjoy.

**Finding the home folder.** It sits four levels deep in the ``whoami()``
response. Without a flow that reach belongs in every script.

**Resolving vocabulary while writing.** Reading, the search resolves
``"Biologie"`` to its URI on its own. Writing, the URI had to be known. This is
where a missing value hurts more: the material is created, just without the
field, and looks complete.

**Saying what did not work.** A partial success is the normal case when several
nodes go into a collection. A flow that reports only the successes reports
success for something that half happened.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..errors import EduSharingError, ValidationError
from .fields import name_from_title, resolve_vocabulary

if TYPE_CHECKING:  # pragma: no cover
    from ..repository import AsyncRepository

__all__ = ["add_material", "build_collection", "delete", "update_material"]

async def add_material(
    repo: AsyncRepository,
    title: str,
    *,
    url: str | None = None,
    parent_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
    keywords: list[str] | None = None,
    collection_id: str | None = None,
    properties: dict[str, Any] | None = None,
    publish: bool = False,
    **aliases: Any,
) -> dict[str, Any]:
    """Create material -- with vocabulary, and optionally straight into a
    collection.

    Args:
        repo: the connection.
        title: the display title. Mandatory; ``cm:name`` is derived from it
            unless ``name`` says otherwise.
        url: web address, for linked material.
        parent_id: where it goes. The user's home folder when omitted.
        name: ``cm:name``, the key inside the parent folder.
        description, keywords: the usual metadata.
        collection_id: put a reference into this collection right away.
        properties: raw edu-sharing properties, for anything not covered.
        **aliases: configured short names -- ``subject="Biologie"`` is resolved
            against this instance's vocabulary.

    Returns:
        ``{id, title, url, parent_id, name, collection, public, unresolved}``.
        ``public`` says whether the material ended up readable without a
        login -- publishing is two steps in edu-sharing, and a caller who
        asked for it needs to know whether both took.

        **Check ``unresolved``.** Values listed there were NOT written; the
        material exists without them and looks complete.

    Raises:
        ValidationError: on an empty title or an unknown short name.
        EduSharingError: for anything the repository refuses.
    """
    if not title or not title.strip():
        raise ValidationError(
            "Material needs a title -- it is what a person sees in the search."
        )

    if parent_id is None:
        identity = await repo.whoami()
        if not identity.home_folder:
            raise EduSharingError(
                "No home folder for this account, so there is nowhere to put the "
                "material. Pass parent_id explicitly. "
                f"(Signed in as {identity.username!r}"
                f"{', anonymously' if identity.is_anonymous else ''}.)"
            )
        parent_id = identity.home_folder

    vocabulary_props, unresolved = await resolve_vocabulary(repo, aliases)
    all_properties = {**(properties or {}), **vocabulary_props}

    direct: dict[str, Any] = {"title": title}
    if url is not None:
        direct["url"] = url
    if description is not None:
        direct["description"] = description
    if keywords:
        direct["keywords"] = keywords

    node = await repo.nodes.create(
        parent_id,
        name=name or name_from_title(title),
        properties=all_properties or None,
        **direct,
    )

    collection: dict[str, Any] | None = None
    if collection_id:
        added = await repo.collections.add(collection_id, node.id)
        collection = {"id": collection_id, "added": added}

    public = node.is_public
    if publish and not public:
        await node.permissions.publish()
        public = True

    return {
        "id": node.id,
        "title": node.title or title,
        "url": node.url,
        "parent_id": parent_id,
        "name": node.name,
        "collection": collection,
        "public": public,
        "unresolved": unresolved,
    }


async def update_material(
    repo: AsyncRepository,
    node_id: str,
    *,
    title: str | None = None,
    url: str | None = None,
    description: str | None = None,
    keywords: list[str] | None = None,
    properties: dict[str, Any] | None = None,
    **aliases: Any,
) -> dict[str, Any]:
    """Change an existing piece of material -- with vocabulary, like creating it.

    Only what is passed is written; everything else stays. The node layer
    verifies the write by reading it back, so a value edu-sharing silently drops
    raises instead of passing as success.

    Args:
        repo: the connection.
        node_id: what to change.
        title, url, description, keywords: the usual metadata.
        properties: raw edu-sharing properties, for anything not covered.
        **aliases: configured short names -- ``subject="Biologie"`` is resolved
            against this instance's vocabulary.

    Returns:
        ``{id, title, url, name, unresolved}`` -- the state after the change.

        **Check ``unresolved``.** Those values were not written, and the rest of
        the change went through regardless.

    Raises:
        ValidationError: when nothing was passed to change.
        SilentDropError: when the repository accepted the write and did not
            store it.
        NotFoundError: when no node carries this id.
    """
    vocabulary_props, unresolved = await resolve_vocabulary(repo, aliases)
    all_properties = {**(properties or {}), **vocabulary_props}

    direct: dict[str, Any] = {}
    for name, value in (("title", title), ("url", url),
                        ("description", description), ("keywords", keywords)):
        if value is not None:
            direct[name] = value

    if not direct and not all_properties:
        # An empty PUT would overwrite nothing and report success -- the caller
        # would believe a change happened. If everything they passed failed to
        # resolve, that is what they need to hear.
        raise ValidationError(
            "Nothing to change: no field was given"
            + (f", and these could not be resolved: {unresolved}" if unresolved else ".")
        )

    node = await repo.nodes.get(node_id)
    updated = await node.update(properties=all_properties or None, **direct)

    return {
        "id": updated.id,
        "title": updated.title,
        "url": updated.url,
        "name": updated.name,
        "unresolved": unresolved,
    }


async def build_collection(
    repo: AsyncRepository,
    title: str,
    *,
    description: str | None = None,
    parent_id: str | None = None,
    node_ids: list[str] | None = None,
    scope: str | None = None,
    publish: bool = False,
) -> dict[str, Any]:
    """Create a collection and fill it in one call.

    Args:
        repo: the connection.
        title: the collection's name.
        description: its description.
        parent_id: parent collection. The collection root when omitted.
        node_ids: material to place inside right away.
        scope: visibility, e.g. ``MY``. The library's default when omitted.

    Returns:
        ``{id, title, url, added, failed, public}``. ``added`` holds the ids that went
        in, ``failed`` holds ``{id, reason}`` for those that did not.

        **The collection exists even when ``failed`` is non-empty.** Placing
        material is one call per node and each can fail on its own; aborting
        halfway would leave a collection nobody asked for.

    Raises:
        EduSharingError: when the collection itself cannot be created.
    """
    kwargs: dict[str, Any] = {}
    if description is not None:
        kwargs["description"] = description
    if parent_id is not None:
        kwargs["parent"] = parent_id
    if scope is not None:
        kwargs["scope"] = scope

    collection = await repo.collections.create(title, **kwargs)

    added: list[str] = []
    failed: list[dict[str, str]] = []
    for node_id in node_ids or []:
        try:
            await repo.collections.add(collection.id, node_id)
        except EduSharingError as exc:
            # Deliberately not aborting: the remaining ids may well work, and a
            # half-filled collection with a named gap beats an unexplained one.
            failed.append({"id": node_id, "reason": str(exc)})
            continue
        added.append(node_id)

    public = collection.is_public
    if publish and not public:
        await collection.permissions.publish()
        public = True

    return {
        "id": collection.id,
        "title": collection.title or title,
        "url": collection.url,
        "added": added,
        "failed": failed,
        "public": public,
    }


async def delete(
    repo: AsyncRepository, node_id: str, *, recycle: bool = True
) -> dict[str, Any]:
    """Delete a node and report what it was.

    Reads the node first so the answer can name it. A bare "done" leaves the
    caller unsure whether the right thing was hit -- and a language model then
    confirms something to a person without knowing what.

    Args:
        repo: the connection.
        node_id: what to delete.
        recycle: into the bin (default) or permanently. The default is the
            reversible one; permanent deletion has to be spelled out.

    Returns:
        ``{id, title, name, type, recycled}`` -- describing what is now gone.

    Raises:
        NotFoundError: when no node carries this id. Nothing is deleted.
        PermissionDeniedError: when it may not be deleted.
    """
    node = await repo.nodes.get(node_id)
    described = {
        "id": node.id,
        "title": node.title,
        "name": node.name,
        "type": node.type,
    }
    await node.delete(recycle=recycle)
    return {**described, "recycled": recycle}
