from fastmcp import FastMCP, Context
from fastmcp.utilities.types import Image
from typing import Any, Dict, List, Literal, Optional, Union
from server.infrastructure.di import (
    get_modeling_handler,
    get_scene_handler,
    get_collection_handler,
    get_material_handler,
    get_uv_handler,
)
from server.application.services.snapshot_diff import get_snapshot_diff_service
from server.infrastructure.tmp_paths import get_viewport_output_paths
from datetime import datetime
import base64

# Initialize MCP Server
mcp = FastMCP("blender-ai-mcp")

# --- Tool Definitions (Adapter Layer) ---

# ... Scene Tools ...
@mcp.tool()
def scene_list_objects(ctx: Context) -> str:
    """
    [SCENE][SAFE][READ-ONLY] Lists all objects in the current Blender scene with their types.
    """
    handler = get_scene_handler()
    try:
        result = handler.list_objects()
        ctx.info(f"Listed {len(result)} objects")
        return str(result)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def scene_delete_object(name: str, ctx: Context) -> str:
    """
    [SCENE][DESTRUCTIVE] Deletes an object from the scene by name.
    This permanently removes the object.
    
    Args:
        name: Name of the object to delete.
    """
    handler = get_scene_handler()
    try:
        return handler.delete_object(name)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def scene_clean_scene(ctx: Context, keep_lights_and_cameras: bool = True) -> str:
    """
    [SCENE][DESTRUCTIVE] Deletes objects from the scene.
    WARNING: If keep_lights_and_cameras=False, deletes EVERYTHING (hard reset).
    
    Args:
        keep_lights_and_cameras: If True (default), keeps Lights and Cameras. 
                                 If False, deletes EVERYTHING (hard reset).
    """
    handler = get_scene_handler()
    try:
        return handler.clean_scene(keep_lights_and_cameras)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def scene_duplicate_object(ctx: Context, name: str, translation: List[float] = None) -> str:
    """
    [SCENE][SAFE] Duplicates an object and optionally moves it.
    
    Args:
        name: Name of the object to duplicate.
        translation: Optional [x, y, z] vector to move the copy.
    """
    handler = get_scene_handler()
    try:
        return str(handler.duplicate_object(name, translation))
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def scene_set_active_object(ctx: Context, name: str) -> str:
    """
    [SCENE][SAFE] Sets the active object.
    Important for operations that work on the "active" object (like adding modifiers).
    
    Args:
        name: Name of the object to set as active.
    """
    handler = get_scene_handler()
    try:
        return handler.set_active_object(name)
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def scene_get_mode(ctx: Context) -> str:
    """
    [SCENE][SAFE][READ-ONLY] Reports the current Blender interaction mode and selection summary.

    Returns a multi-line description with mode, active object, and selected objects to help
    AI agents branch logic without guessing the context.
    """
    handler = get_scene_handler()
    try:
        response = handler.get_mode()
    except RuntimeError as e:
        return str(e)

    selected_names = response.get("selected_object_names") or []
    selected = ", ".join(selected_names) if selected_names else "None"
    active_type = response.get("active_object_type")
    active_suffix = f" ({active_type})" if active_type else ""
    return (
        "Blender Context Snapshot:\n"
        f"- Mode: {response.get('mode', 'UNKNOWN')}\n"
        f"- Active Object: {response.get('active_object') or 'None'}{active_suffix}\n"
        f"- Selected Objects ({response.get('selection_count', 0)}): {selected}"
    )


@mcp.tool()
def scene_list_selection(ctx: Context) -> str:
    """
    [SCENE][SAFE][READ-ONLY] Lists the current selection in Object or Edit Mode.

    Provides counts for selected objects and, when in Edit Mode, counts of selected
    vertices/edges/faces. Useful for verifying assumptions before destructive edits.
    """
    handler = get_scene_handler()
    try:
        summary = handler.list_selection()
    except RuntimeError as e:
        return str(e)

    selected_names = summary.get("selected_object_names") or []
    selected = ", ".join(selected_names) if selected_names else "None"
    parts = [
        "Selection Summary:",
        f"- Mode: {summary.get('mode', 'UNKNOWN')}",
        f"- Objects Selected ({summary.get('selection_count', 0)}): {selected}",
    ]

    if summary.get("edit_mode_vertex_count") is not None:
        parts.append(
            "- Edit Mode Counts: V={} E={} F={}".format(
                summary.get("edit_mode_vertex_count", 0),
                summary.get("edit_mode_edge_count", 0),
                summary.get("edit_mode_face_count", 0),
            )
        )

    return "\n".join(parts)


@mcp.tool()
def scene_inspect_object(ctx: Context, name: str) -> str:
    """
    [SCENE][SAFE][READ-ONLY] Provides a detailed report for a single object (transform, collections, materials, modifiers, mesh stats).
    """
    handler = get_scene_handler()
    try:
        report = handler.inspect_object(name)
    except RuntimeError as e:
        msg = str(e)
        if "not found" in msg.lower():
            return f"{msg}. Use scene_list_objects to verify the name."
        return msg

    lines = [
        f"Object: {report.get('object_name')} ({report.get('type')})",
        f"Location: {report.get('location')}",
        f"Rotation: {report.get('rotation')}",
        f"Scale: {report.get('scale')}",
        f"Dimensions: {report.get('dimensions')}",
        f"Collections: {', '.join(report.get('collections') or ['<none>'])}",
    ]

    material_slots = report.get("material_slots") or []
    if material_slots:
        slot_lines = [
            f"    #{slot['slot_index']}: {slot.get('material_name') or 'None'}"
            for slot in material_slots
        ]
        lines.append("Materials:\n" + "\n".join(slot_lines))
    else:
        lines.append("Materials: <none>")

    modifiers = report.get("modifiers") or []
    if modifiers:
        mod_lines = [
            f"    {mod.get('name')} ({mod.get('type')}), viewport={mod.get('show_viewport')}, render={mod.get('show_render')}"
            for mod in modifiers
        ]
        lines.append("Modifiers:\n" + "\n".join(mod_lines))
    else:
        lines.append("Modifiers: <none>")

    mesh_stats = report.get("mesh_stats")
    if mesh_stats:
        lines.append(
            "Mesh Stats: V={vertices}, E={edges}, F={faces}, T={triangles}".format(
                vertices=mesh_stats.get("vertices"),
                edges=mesh_stats.get("edges"),
                faces=mesh_stats.get("faces"),
                triangles=mesh_stats.get("triangles"),
            )
        )
    else:
        lines.append("Mesh Stats: <not a mesh>")

    custom_props = report.get("custom_properties") or {}
    if custom_props:
        prop_lines = [f"    {k}: {v}" for k, v in custom_props.items()]
        lines.append("Custom Properties:\n" + "\n".join(prop_lines))
    else:
        lines.append("Custom Properties: <none>")

    return "\n".join(lines)


@mcp.tool()
def scene_get_viewport(
    ctx: Context,
    width: int = 1024,
    height: int = 768,
    shading: str = "SOLID",
    camera_name: str = None,
    focus_target: str = None,
    output_mode: Literal["IMAGE", "BASE64", "FILE", "MARKDOWN"] = "IMAGE",
) -> Union[Image, str]:
    """Get a visual preview of the scene (OpenGL Viewport Render).

    The tool can return the viewport in multiple formats, controlled by
    ``output_mode``:

    * ``IMAGE`` (default): Returns a FastMCP ``Image`` resource (best for
      clients that natively support image resources, like Cline).
    * ``BASE64``: Returns the raw base64-encoded JPEG data as a string for
      direct consumption by Vision modules.
    * ``FILE``: Saves the image to a temp directory and returns a description
      containing **host-visible** file paths, without markdown or data URLs.
    * ``MARKDOWN``: Saves the image to a temp directory and returns rich
      markdown with an inline ``data:`` URL preview plus host-visible paths.

    Args:
        width: Image width in pixels.
        height: Image height in pixels.
        shading: Viewport shading mode ('WIREFRAME', 'SOLID', 'MATERIAL', 'RENDERED').
        camera_name: Name of the camera to use. If None or "USER_PERSPECTIVE", uses a temporary
            camera.
        focus_target: Name of the object to focus on. Only works if camera_name is
            None/"USER_PERSPECTIVE".
        output_mode: Output format selector: "IMAGE", "BASE64", "FILE", or "MARKDOWN".
    """
    handler = get_scene_handler()
    try:
        # Domain/Application return base64 only; formatting happens here.
        b64_data = handler.get_viewport(width, height, shading, camera_name, focus_target)
    except RuntimeError as e:
        return str(e)

    mode = (output_mode or "IMAGE").upper()

    if mode == "IMAGE":
        image_bytes = base64.b64decode(b64_data)
        return Image(data=image_bytes, format="jpeg")

    if mode == "BASE64":
        return b64_data

    if mode in {"FILE", "MARKDOWN"}:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"viewport_{timestamp}.jpg"
        internal_file, internal_latest, external_file, external_latest = get_viewport_output_paths(
            filename
        )
        image_bytes = base64.b64decode(b64_data)
        internal_file.write_bytes(image_bytes)
        internal_latest.write_bytes(image_bytes)

        header = (
            f"Viewport render saved.\n\n"
            f"Timestamped file: {external_file}\n"
            f"Latest file: {external_latest}\n\n"
            f"Resolution: {width}x{height}, shading: {shading}."
        )

        if mode == "FILE":
            return header

        data_url = f"data:image/jpeg;base64,{b64_data}"
        return (
            f"Viewport render saved to: {external_latest}\n\n"
            f"**Preview ({width}x{height}, {shading} mode):**\n\n"
            f"![Viewport]({data_url})\n\n"
            f"*Note: If you cannot see the image above, open the file at: {external_latest}*"
        )

    return (
        f"Invalid output_mode '{mode}'. Allowed values are: IMAGE, BASE64, FILE, MARKDOWN."
    )

@mcp.tool()
def scene_snapshot_state(
    ctx: Context,
    include_mesh_stats: bool = False,
    include_materials: bool = False
) -> str:
    """
    [SCENE][SAFE][READ-ONLY] Captures a lightweight JSON snapshot of the scene state.

    Returns a serialized snapshot containing object transforms, hierarchy, modifiers,
    and selection state. Includes a SHA256 hash for change detection. Large payloads
    are possible when optional flags are enabled.

    Args:
        include_mesh_stats: If True, includes vertex/edge/face counts for mesh objects.
        include_materials: If True, includes material names assigned to objects.
    """
    handler = get_scene_handler()
    try:
        result = handler.snapshot_state(
            include_mesh_stats=include_mesh_stats,
            include_materials=include_materials
        )
        import json

        snapshot = result.get("snapshot", {})
        snapshot_hash = result.get("hash", "unknown")
        object_count = snapshot.get("object_count", 0)
        timestamp = snapshot.get("timestamp", "unknown")

        # Format summary
        summary = (
            f"Scene Snapshot Captured:\n"
            f"- Timestamp: {timestamp}\n"
            f"- Objects: {object_count}\n"
            f"- Hash: {snapshot_hash[:16]}...\n"
            f"- Active Object: {snapshot.get('active_object') or 'None'}\n"
            f"- Mode: {snapshot.get('mode', 'UNKNOWN')}\n\n"
            f"Full snapshot (JSON):\n{json.dumps(snapshot, indent=2)}"
        )

        ctx.info(f"Snapshot captured: {object_count} objects, hash={snapshot_hash[:8]}")
        return summary
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def scene_compare_snapshot(
    ctx: Context,
    baseline_snapshot: str,
    target_snapshot: str,
    ignore_minor_transforms: float = 0.0
) -> str:
    """
    [SCENE][SAFE][READ-ONLY] Compares two scene snapshots and returns a diff summary.

    Takes two JSON snapshot strings (from scene_snapshot_state) and computes
    the differences: objects added/removed, and modifications to transforms,
    modifiers, and materials.

    Args:
        baseline_snapshot: JSON string of the baseline snapshot
        target_snapshot: JSON string of the target snapshot
        ignore_minor_transforms: Threshold for ignoring small transform changes (default 0.0)
    """
    diff_service = get_snapshot_diff_service()

    try:
        result = diff_service.compare_snapshots(
            baseline_snapshot=baseline_snapshot,
            target_snapshot=target_snapshot,
            ignore_minor_transforms=ignore_minor_transforms
        )
    except ValueError as e:
        return f"Error: {str(e)}"

    # Format the diff summary
    added = result.get("objects_added", [])
    removed = result.get("objects_removed", [])
    modified = result.get("objects_modified", [])
    has_changes = result.get("has_changes", False)

    if not has_changes:
        return "No changes detected between snapshots."

    lines = [
        "Snapshot Comparison:",
        f"- Baseline: {result.get('baseline_timestamp')} (hash: {result.get('baseline_hash', 'unknown')[:16]}...)",
        f"- Target: {result.get('target_timestamp')} (hash: {result.get('target_hash', 'unknown')[:16]}...)",
        ""
    ]

    if added:
        lines.append(f"Objects Added ({len(added)}):")
        for obj_name in added:
            lines.append(f"  + {obj_name}")
        lines.append("")

    if removed:
        lines.append(f"Objects Removed ({len(removed)}):")
        for obj_name in removed:
            lines.append(f"  - {obj_name}")
        lines.append("")

    if modified:
        lines.append(f"Objects Modified ({len(modified)}):")
        for mod in modified:
            obj_name = mod.get("object_name")
            changes = mod.get("changes", [])
            lines.append(f"  ~ {obj_name}:")
            for change in changes:
                prop = change.get("property")
                old_val = change.get("old_value")
                new_val = change.get("new_value")
                lines.append(f"      {prop}: {old_val} → {new_val}")
        lines.append("")

    summary = "\n".join(lines)
    ctx.info(f"Snapshot diff: +{len(added)} -{len(removed)} ~{len(modified)}")
    return summary

@mcp.tool()
def scene_inspect_material_slots(
    ctx: Context,
    material_filter: Optional[str] = None,
    include_empty_slots: bool = True
) -> str:
    """
    [SCENE][SAFE][READ-ONLY] Audits material slot assignments across the entire scene.

    Provides a comprehensive view of how materials are distributed across all objects,
    including empty slots, missing materials, and assignment statistics. Useful for
    identifying material issues before rendering or export.

    Args:
        material_filter: Optional material name to filter results
        include_empty_slots: If True, includes slots with no material assigned
    """
    handler = get_scene_handler()
    try:
        result = handler.inspect_material_slots(
            material_filter=material_filter,
            include_empty_slots=include_empty_slots
        )
        import json

        total = result.get("total_slots", 0)
        assigned = result.get("assigned_slots", 0)
        empty = result.get("empty_slots", 0)
        warnings = result.get("warnings", [])
        slots = result.get("slots", [])

        # Format summary
        lines = [
            "Material Slot Audit:",
            f"- Total Slots: {total}",
            f"- Assigned: {assigned}",
            f"- Empty: {empty}",
        ]

        if material_filter:
            lines.append(f"- Filter: '{material_filter}'")

        if warnings:
            lines.append(f"\nWarnings ({len(warnings)}):")
            for warning in warnings:
                lines.append(f"  ! {warning}")

        if slots:
            lines.append(f"\nSlot Details ({len(slots)} slots):")
            for slot in slots[:20]:  # Limit to first 20 for readability
                obj_name = slot.get("object_name")
                slot_idx = slot.get("slot_index")
                mat_name = slot.get("material_name") or "EMPTY"
                slot_name = slot.get("slot_name", "")
                lines.append(f"  [{obj_name}][{slot_idx}] {slot_name}: {mat_name}")

            if len(slots) > 20:
                lines.append(f"  ... and {len(slots) - 20} more slots")

        lines.append(f"\nFull data (JSON):\n{json.dumps(result, indent=2)}")

        summary = "\n".join(lines)
        ctx.info(f"Material slot audit: {total} slots ({assigned} assigned, {empty} empty)")
        return summary
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def scene_create_light(
    ctx: Context,
    type: str,
    energy: float = 1000.0,
    color: List[float] = (1.0, 1.0, 1.0),
    location: List[float] = (0.0, 0.0, 5.0),
    name: Optional[str] = None
) -> str:
    """
    [SCENE][SAFE] Creates a light source.

    Args:
        type: 'POINT', 'SUN', 'SPOT', 'AREA'.
        energy: Power in Watts.
        color: [r, g, b] (0.0 to 1.0).
        location: [x, y, z].
        name: Optional custom name.
    """
    handler = get_scene_handler()
    try:
        return handler.create_light(type, energy, color, location, name)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def scene_create_camera(
    ctx: Context,
    location: List[float],
    rotation: List[float],
    lens: float = 50.0,
    clip_start: Optional[float] = None,
    clip_end: Optional[float] = None,
    name: Optional[str] = None
) -> str:
    """
    [SCENE][SAFE] Creates a camera object.

    Args:
        location: [x, y, z].
        rotation: [x, y, z] Euler angles in radians.
        lens: Focal length in mm.
        clip_start: Near clipping distance.
        clip_end: Far clipping distance.
        name: Optional custom name.
    """
    handler = get_scene_handler()
    try:
        return handler.create_camera(location, rotation, lens, clip_start, clip_end, name)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def scene_create_empty(
    ctx: Context,
    type: str,
    size: float = 1.0,
    location: List[float] = (0.0, 0.0, 0.0),
    name: Optional[str] = None
) -> str:
    """
    [SCENE][SAFE] Creates an Empty object (useful for grouping or tracking).

    Args:
        type: 'PLAIN_AXES', 'ARROWS', 'SINGLE_ARROW', 'CIRCLE', 'CUBE', 'SPHERE', 'CONE', 'IMAGE'.
        size: Display size.
        location: [x, y, z].
        name: Optional custom name.
    """
    handler = get_scene_handler()
    try:
        return handler.create_empty(type, size, location, name)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def scene_set_mode(ctx: Context, mode: str) -> str:
    """
    [SCENE][SAFE] Sets the interaction mode (OBJECT, EDIT, SCULPT, POSE, WEIGHT_PAINT, TEXTURE_PAINT).
    
    Args:
        mode: The target mode (case-insensitive).
    """
    handler = get_scene_handler()
    try:
        return handler.set_mode(mode)
    except RuntimeError as e:
        return str(e)

# ... Collection Tools ...

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

# ... Material Tools ...

@mcp.tool()
def material_list(ctx: Context, include_unassigned: bool = True) -> str:
    """
    [MATERIAL][SAFE][READ-ONLY] Lists materials with shader parameters and assignment counts.

    Args:
        include_unassigned: If True, includes materials not assigned to any object
    """
    handler = get_material_handler()
    try:
        materials = handler.list_materials(include_unassigned=include_unassigned)

        if not materials:
            return "No materials found in the scene."

        lines = [f"Materials ({len(materials)}):"]
        for mat in materials:
            name = mat["name"]
            uses_nodes = mat.get("use_nodes", False)
            assigned = mat.get("assigned_object_count", 0)

            details = []
            if not uses_nodes:
                details.append("legacy")
            if assigned == 0:
                details.append("unassigned")

            detail_str = f" [{', '.join(details)}]" if details else ""

            lines.append(f"  • {name} (objects: {assigned}){detail_str}")

            # Add shader params if available
            if "base_color" in mat:
                rgb = mat["base_color"]
                lines.append(f"      Color: RGB{rgb}, Roughness: {mat.get('roughness', 'N/A')}, Metallic: {mat.get('metallic', 'N/A')}")

        ctx.info(f"Listed {len(materials)} materials")
        return "\n".join(lines)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def material_list_by_object(ctx: Context, object_name: str, include_indices: bool = False) -> str:
    """
    [MATERIAL][SAFE][READ-ONLY] Lists material slots for a given object.

    Args:
        object_name: Name of the object to query
        include_indices: If True, attempts to include face-level assignment info
    """
    handler = get_material_handler()
    try:
        result = handler.list_by_object(object_name=object_name, include_indices=include_indices)

        slots = result.get("slots", [])
        slot_count = result.get("slot_count", 0)

        if slot_count == 0:
            return f"Object '{object_name}' has no material slots."

        lines = [
            f"Object: {object_name}",
            f"Material Slots ({slot_count}):"
        ]

        for slot in slots:
            mat_name = slot.get("material_name") or "<empty>"
            idx = slot.get("slot_index")
            uses_nodes = " [nodes]" if slot.get("uses_nodes") else ""

            lines.append(f"  [{idx}] {slot.get('slot_name')}: {mat_name}{uses_nodes}")

            if "note" in slot:
                lines.append(f"      Note: {slot['note']}")

        ctx.info(f"Listed {slot_count} material slots for '{object_name}'")
        return "\n".join(lines)
    except RuntimeError as e:
        msg = str(e)
        if "not found" in msg.lower():
            return f"{msg}. Use scene_list_objects to verify the name."
        return msg

# ... UV Tools ...

@mcp.tool()
def uv_list_maps(
    ctx: Context,
    object_name: str,
    include_island_counts: bool = False
) -> str:
    """
    [UV][SAFE][READ-ONLY] Lists UV maps on a mesh object.

    Reports UV map information including names, active flags, and loop counts.
    Helps plan UV workflows and verify texture coordinate setup.

    Args:
        object_name: Name of the mesh object to query
        include_island_counts: If True, includes UV loop counts (island counts not yet implemented)
    """
    handler = get_uv_handler()
    try:
        result = handler.list_maps(
            object_name=object_name,
            include_island_counts=include_island_counts
        )

        obj_name = result.get("object_name")
        uv_map_count = result.get("uv_map_count", 0)
        uv_maps = result.get("uv_maps", [])

        if uv_map_count == 0:
            return f"Object '{obj_name}' has no UV maps."

        lines = [
            f"Object: {obj_name}",
            f"UV Maps ({uv_map_count}):"
        ]

        for uv_map in uv_maps:
            name = uv_map.get("name")
            is_active = uv_map.get("is_active", False)
            is_active_render = uv_map.get("is_active_render", False)

            flags = []
            if is_active:
                flags.append("active")
            if is_active_render:
                flags.append("active_render")

            flag_str = f" [{', '.join(flags)}]" if flags else ""
            lines.append(f"  - {name}{flag_str}")

            if include_island_counts:
                uv_loop_count = uv_map.get("uv_loop_count")
                island_count = uv_map.get("island_count")
                if uv_loop_count is not None:
                    lines.append(f"      UV loops: {uv_loop_count}")
                if island_count is not None:
                    lines.append(f"      Islands: {island_count}")
                else:
                    lines.append(f"      Islands: (not implemented)")

        ctx.info(f"Listed {uv_map_count} UV maps for '{obj_name}'")
        return "\n".join(lines)
    except RuntimeError as e:
        msg = str(e)
        if "not found" in msg.lower() or "not a MESH" in msg:
            return f"{msg}. Use scene_list_objects to verify the object name and type."
        return msg

# ... Modeling Tools ...

@mcp.tool()
def modeling_create_primitive(
    ctx: Context,
    primitive_type: str, 
    radius: float = 1.0, 
    size: float = 2.0, 
    location: List[float] = (0.0, 0.0, 0.0), 
    rotation: List[float] = (0.0, 0.0, 0.0),
    name: str = None
) -> str:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Creates a 3D primitive object.
    
    Args:
        primitive_type: "Cube", "Sphere", "Cylinder", "Plane", "Cone", "Monkey", "Torus".
        radius: Radius for Sphere/Cylinder/Cone.
        size: Size for Cube/Plane/Monkey.
        location: [x, y, z] coordinates.
        rotation: [rx, ry, rz] rotation in radians.
        name: Optional name for the new object.
    """
    handler = get_modeling_handler()
    try:
        return handler.create_primitive(primitive_type, radius, size, location, rotation, name)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def modeling_transform_object(
    ctx: Context,
    name: str, 
    location: Optional[List[float]] = None, 
    rotation: Optional[List[float]] = None, 
    scale: Optional[List[float]] = None
) -> str:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Transforms (move, rotate, scale) an existing object.
    
    Args:
        name: Name of the object.
        location: New [x, y, z] coordinates (optional).
        rotation: New [rx, ry, rz] rotation in radians (optional).
        scale: New [sx, sy, sz] scale factors (optional).
    """
    handler = get_modeling_handler()
    try:
        return handler.transform_object(name, location, rotation, scale)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def modeling_add_modifier(
    ctx: Context,
    name: str, 
    modifier_type: str, 
    properties: Dict[str, Any] = None
) -> str:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Adds a modifier to an object.
    Preferred method for booleans, subdivision, mirroring (non-destructive stack).
    
    Args:
        name: Object name.
        modifier_type: Type of modifier (e.g., 'SUBSURF', 'BEVEL', 'MIRROR', 'BOOLEAN').
        properties: Dictionary of modifier properties to set (e.g., {'levels': 2}).
    """
    handler = get_modeling_handler()
    try:
        return handler.add_modifier(name, modifier_type, properties)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def modeling_apply_modifier(
    ctx: Context,
    name: str, 
    modifier_name: str
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Applies a modifier, making its changes permanent to the mesh.
    
    Args:
        name: Object name.
        modifier_name: The name of the modifier to apply.
    """
    handler = get_modeling_handler()
    try:
        return handler.apply_modifier(name, modifier_name)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def modeling_convert_to_mesh(
    ctx: Context,
    name: str
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Converts a non-mesh object (Curve, Text, Surface) to a mesh.
    
    Args:
        name: The name of the object to convert.
    """
    handler = get_modeling_handler()
    try:
        return handler.convert_to_mesh(name)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def modeling_join_objects(
    ctx: Context,
    object_names: List[str]
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Joins multiple mesh objects into a single mesh.
    IMPORTANT: The LAST object in the list becomes the Active Object (Base).
    
    Args:
        object_names: A list of names of the objects to join.
    """
    handler = get_modeling_handler()
    try:
        return handler.join_objects(object_names)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def modeling_separate_object(
    ctx: Context,
    name: str,
    type: str = "LOOSE"
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Separates a mesh into new objects (LOOSE, SELECTED, MATERIAL).
    
    Args:
        name: The name of the object to separate.
        type: The separation method: "LOOSE", "SELECTED", or "MATERIAL".
    """
    handler = get_modeling_handler()
    try:
        result = handler.separate_object(name, type)
        return str(result)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def modeling_list_modifiers(
    ctx: Context,
    name: str
) -> str:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Lists all modifiers currently on the specified object.
    
    Args:
        name: The name of the object.
    """
    handler = get_modeling_handler()
    try:
        modifiers = handler.get_modifiers(name)
        return str(modifiers)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def modeling_set_origin(
    ctx: Context,
    name: str,
    type: str
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Sets the origin point of an object.
    
    Args:
        name: Object name.
        type: Origin type (e.g., 'ORIGIN_GEOMETRY', 'ORIGIN_CURSOR', 'ORIGIN_CENTER_OF_MASS').
    """
    handler = get_modeling_handler()
    try:
        return handler.set_origin(name, type)
    except RuntimeError as e:
        return str(e)

# ... Mesh Tools (Edit Mode) ...

from server.infrastructure.di import get_mesh_handler

@mcp.tool()
def mesh_select_all(ctx: Context, deselect: bool = False) -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Selects or deselects all geometry elements.
    
    Args:
        deselect: If True, deselects all. If False (default), selects all.
    """
    handler = get_mesh_handler()
    try:
        return handler.select_all(deselect)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_delete_selected(ctx: Context, type: str = 'VERT') -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Deletes selected geometry elements.
    
    Args:
        type: 'VERT', 'EDGE', 'FACE'.
    """
    handler = get_mesh_handler()
    try:
        return handler.delete_selected(type)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_select_by_index(ctx: Context, indices: List[int], type: str = 'VERT', selection_mode: str = 'SET') -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Selects specific geometry elements by index.
    Uses BMesh for precise 0-based indexing.
    
    Args:
        indices: List of integer indices.
        type: 'VERT', 'EDGE', 'FACE'.
        selection_mode: 'SET' (replace), 'ADD' (extend), 'SUBTRACT' (deselect).
    """
    handler = get_mesh_handler()
    try:
        return handler.select_by_index(indices, type, selection_mode)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_extrude_region(ctx: Context, move: List[float] = None) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Extrudes selected geometry.
    WARNING: If 'move' is None, new geometry is created in-place (overlapping).
    Always provide 'move' vector or follow up with transform.
    
    Args:
        move: Optional [x, y, z] vector to move extruded region.
    """
    handler = get_mesh_handler()
    try:
        return handler.extrude_region(move)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_fill_holes(ctx: Context) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Fills holes by creating faces from selected edges/vertices.
    Equivalent to pressing 'F' key in Blender.
    """
    handler = get_mesh_handler()
    try:
        return handler.fill_holes()
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_bevel(
    ctx: Context,
    offset: float = 0.1,
    segments: int = 1,
    profile: float = 0.5,
    affect: str = 'EDGES'
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Bevels selected edges or vertices.
    
    Args:
        offset: Size of the bevel (distance/width).
        segments: Number of segments (rounding).
        profile: Shape of the bevel (0.5 is round).
        affect: 'EDGES' or 'VERTICES'.
    """
    handler = get_mesh_handler()
    try:
        return handler.bevel(offset, segments, profile, affect)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_loop_cut(
    ctx: Context,
    number_cuts: int = 1,
    smoothness: float = 0.0
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Adds cuts to mesh geometry.
    IMPORTANT: Uses 'subdivide' on SELECTED edges.
    Select edges perpendicular to desired cut direction first.
    
    Args:
        number_cuts: Number of cuts to make.
        smoothness: Smoothness of the subdivision.
    """
    handler = get_mesh_handler()
    try:
        return handler.loop_cut(number_cuts, smoothness)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_inset(
    ctx: Context,
    thickness: float = 0.0,
    depth: float = 0.0
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Insets selected faces (creates smaller faces inside).
    
    Args:
        thickness: Amount to inset.
        depth: Amount to move the inset face in/out.
    """
    handler = get_mesh_handler()
    try:
        return handler.inset(thickness, depth)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_boolean(
    ctx: Context,
    operation: str = 'DIFFERENCE',
    solver: str = 'FAST'
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Boolean operation on selected geometry.
    Formula: Unselected - Selected (for DIFFERENCE).
    TIP: For object-level booleans, prefer 'modeling_add_modifier(BOOLEAN)' (safer).
    
    Workflow:
      1. Select 'Cutter' geometry.
      2. Deselect 'Base' geometry.
      3. Run tool.
    
    Args:
        operation: 'INTERSECT', 'UNION', 'DIFFERENCE'.
        solver: 'FAST' or 'EXACT'.
    """
    handler = get_mesh_handler()
    try:
        return handler.boolean(operation, solver)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_merge_by_distance(
    ctx: Context,
    distance: float = 0.001
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Merges vertices within threshold distance.
    Useful for cleaning up geometry after imports or boolean ops.
    
    Args:
        distance: Threshold distance to merge.
    """
    handler = get_mesh_handler()
    try:
        return handler.merge_by_distance(distance)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_subdivide(
    ctx: Context,
    number_cuts: int = 1,
    smoothness: float = 0.0
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Subdivides selected geometry.
    
    Args:
        number_cuts: Number of cuts.
        smoothness: Smoothness factor (0.0 to 1.0).
    """
    handler = get_mesh_handler()
    try:
        return handler.subdivide(number_cuts, smoothness)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_smooth(
    ctx: Context,
    iterations: int = 1,
    factor: float = 0.5
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE] Smooths selected vertices.
    Uses Laplacian smoothing to refine organic shapes and remove hard edges.
    
    Args:
        iterations: Number of smoothing passes (1-100). More = smoother
        factor: Smoothing strength (0.0-1.0). 0=no effect, 1=maximum smoothing
    """
    handler = get_mesh_handler()
    try:
        return handler.smooth_vertices(iterations, factor)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_flatten(
    ctx: Context,
    axis: str
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Flattens selected vertices to plane.
    Aligns vertices perpendicular to chosen axis (X: YZ plane, Y: XZ plane, Z: XY plane).
    
    Args:
        axis: Axis to flatten along ("X", "Y", or "Z")
    """
    handler = get_mesh_handler()
    try:
        return handler.flatten_vertices(axis)
    except RuntimeError as e:
        return str(e)

def run():
    """Starts the MCP server."""
    mcp.run()