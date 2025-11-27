from fastmcp import Context
from server.adapters.mcp.instance import mcp
from server.infrastructure.di import get_collection_handler

@mcp.tool()
def collection_list(ctx: Context, include_objects: bool = False) -> str:
    """
    [COLLECTION][SAFE][READ-ONLY] Lists all collections with hierarchy information.

    Returns collection names, parent relationships, object counts, and visibility flags.
    Optionally includes object names within each collection.

    Args:
        include_objects: If True, includes object names within each collection.
    """
    handler = get_collection_handler()
    try:
        collections = handler.list_collections(include_objects=include_objects)

        if not collections:
            return "No collections found in the scene."

        lines = [f"Collections ({len(collections)}):"]

        for col in collections:
            parent = col.get("parent") or "<root>"
            obj_count = col.get("object_count", 0)
            child_count = col.get("child_count", 0)

            # Build visibility info
            visibility = []
            if col.get("hide_viewport"):
                visibility.append("hidden-viewport")
            if col.get("hide_render"):
                visibility.append("hidden-render")
            if col.get("hide_select"):
                visibility.append("unselectable")

            vis_str = f" [{', '.join(visibility)}]" if visibility else ""

            lines.append(
                f"  • {col['name']} (parent: {parent}, objects: {obj_count}, children: {child_count}){vis_str}"
            )

            # Optionally list objects
            if include_objects and col.get("objects"):
                obj_list = ", ".join(col["objects"])
                lines.append(f"      Objects: {obj_list}")

        ctx.info(f"Listed {len(collections)} collections")
        return "\n".join(lines)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def collection_list_objects(
    ctx: Context,
    collection_name: str,
    recursive: bool = True,
    include_hidden: bool = False
) -> str:
    """
    [COLLECTION][SAFE][READ-ONLY] Lists objects inside a collection.

    Returns all objects contained within the specified collection. Optionally
    includes objects from child collections (recursive) and hidden objects.

    Args:
        collection_name: Name of the collection to query
        recursive: If True, includes objects from child collections (default True)
        include_hidden: If True, includes hidden objects (default False)
    """
    handler = get_collection_handler()
    try:
        result = handler.list_objects(
            collection_name=collection_name,
            recursive=recursive,
            include_hidden=include_hidden
        )

        objects = result.get("objects", [])
        object_count = result.get("object_count", 0)

        if object_count == 0:
            return f"Collection '{collection_name}' contains no objects (recursive={recursive}, include_hidden={include_hidden})."

        lines = [
            f"Collection: {collection_name}",
            f"Objects ({object_count}, recursive={recursive}, hidden={include_hidden}):"
        ]

        for obj in objects:
            visibility = []
            if not obj.get("visible_viewport"):
                visibility.append("hidden-viewport")
            if not obj.get("visible_render"):
                visibility.append("hidden-render")

            vis_str = f" [{', '.join(visibility)}]" if visibility else ""
            selected_str = " [selected]" if obj.get("selected") else ""

            lines.append(
                f"  • {obj['name']} ({obj['type']}) @ {obj['location']}{vis_str}{selected_str}"
            )

        ctx.info(f"Listed {object_count} objects from collection '{collection_name}'")
        return "\n".join(lines)
    except RuntimeError as e:
        msg = str(e)
        if "not found" in msg.lower():
            return f"{msg}. Use collection_list to see available collections."
        return msg