import base64
from datetime import datetime
from typing import List, Literal, Optional, Union
from fastmcp import Context
from fastmcp.utilities.types import Image
from server.adapters.mcp.instance import mcp
from server.adapters.mcp.utils import parse_coordinate
from server.infrastructure.di import get_scene_handler
from server.application.services.snapshot_diff import get_snapshot_diff_service
from server.infrastructure.tmp_paths import get_viewport_output_paths

# ... Scene Tools ...
@mcp.tool()
def scene_list_objects(ctx: Context) -> str:
    """
    [SCENE][SAFE][READ-ONLY] Lists all objects in the current Blender scene with their types.

    Workflow: READ-ONLY | START → understand scene
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

    Workflow: DESTRUCTIVE | BEFORE → scene_list_objects

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

    Workflow: START → fresh scene | AFTER → modeling_create_primitive

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
def scene_duplicate_object(ctx: Context, name: str, translation: Union[str, List[float], None] = None) -> str:
    """
    [SCENE][SAFE] Duplicates an object and optionally moves it.

    Workflow: AFTER → scene_set_active | USE FOR → copies with offset

    Args:
        name: Name of the object to duplicate.
        translation: Optional [x, y, z] vector to move the copy. Can be a list or string '[1.0, 2.0, 3.0]'.
    """
    handler = get_scene_handler()
    try:
        parsed_translation = parse_coordinate(translation)
        return str(handler.duplicate_object(name, parsed_translation))
    except (RuntimeError, ValueError) as e:
        return str(e)

@mcp.tool()
def scene_set_active_object(ctx: Context, name: str) -> str:
    """
    [SCENE][SAFE] Sets the active object.
    Important for operations that work on the "active" object (like adding modifiers).

    Workflow: BEFORE → any object operation | REQUIRED BY → modifiers, transforms

    Args:
        name: Name of the object to set as active.
    """
    handler = get_scene_handler()
    try:
        return handler.set_active_object(name)
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def scene_context(
    ctx: Context,
    action: Literal["mode", "selection"]
) -> str:
    """
    [SCENE][READ-ONLY][SAFE] Quick context queries for scene state.

    Actions:
    - "mode": Returns current Blender mode, active object, selection count.
    - "selection": Returns selected objects list + edit mode vertex/edge/face counts.

    Workflow: READ-ONLY | FIRST STEP → check context before any operation

    Examples:
        scene_context(action="mode")
        scene_context(action="selection")
    """
    if action == "mode":
        return _scene_get_mode(ctx)
    elif action == "selection":
        return _scene_list_selection(ctx)
    else:
        return f"Unknown action '{action}'. Valid actions: mode, selection"


# Internal function - exposed via scene_context mega tool
def _scene_get_mode(ctx: Context) -> str:
    """
    [SCENE][SAFE][READ-ONLY] Reports the current Blender interaction mode and selection summary.

    Workflow: READ-ONLY | USE → check context before operations

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


# Internal function - exposed via scene_context mega tool
def _scene_list_selection(ctx: Context) -> str:
    """
    [SCENE][SAFE][READ-ONLY] Lists the current selection in Object or Edit Mode.

    Workflow: READ-ONLY | USE → verify selection state

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
def scene_inspect(
    ctx: Context,
    action: Literal["object", "topology", "modifiers", "materials"],
    object_name: Optional[str] = None,
    detailed: bool = False,
    include_disabled: bool = True,
    material_filter: Optional[str] = None,
    include_empty_slots: bool = True
) -> str:
    """
    [SCENE][READ-ONLY][SAFE] Detailed inspection queries for objects and scene.

    Actions and required parameters:
    - "object": Requires object_name. Returns transform, collections, materials, modifiers, mesh stats.
    - "topology": Requires object_name. Returns vertex/edge/face/tri/quad/ngon counts. Optional: detailed=True for non-manifold checks.
    - "modifiers": Optional object_name (None scans all). Returns modifier stacks. Optional: include_disabled=False.
    - "materials": No params required. Returns material slot audit. Optional: material_filter, include_empty_slots.

    Workflow: READ-ONLY | USE → detailed analysis before export or debugging

    Examples:
        scene_inspect(action="object", object_name="Cube")
        scene_inspect(action="topology", object_name="Cube", detailed=True)
        scene_inspect(action="modifiers", object_name="Cube")
        scene_inspect(action="modifiers")  # scans all objects
        scene_inspect(action="materials", material_filter="Wood")
    """
    if action == "object":
        if object_name is None:
            return "Error: 'object' action requires 'object_name' parameter."
        return _scene_inspect_object(ctx, object_name)
    elif action == "topology":
        if object_name is None:
            return "Error: 'topology' action requires 'object_name' parameter."
        return _scene_inspect_mesh_topology(ctx, object_name, detailed)
    elif action == "modifiers":
        return _scene_inspect_modifiers(ctx, object_name, include_disabled)
    elif action == "materials":
        return _scene_inspect_material_slots(ctx, material_filter, include_empty_slots)
    else:
        return f"Unknown action '{action}'. Valid actions: object, topology, modifiers, materials"


# Internal function - exposed via scene_inspect mega tool
def _scene_inspect_object(ctx: Context, name: str) -> str:
    """
    [SCENE][SAFE][READ-ONLY] Provides a detailed report for a single object (transform, collections, materials, modifiers, mesh stats).

    Workflow: READ-ONLY | USE → detailed object audit
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

    Workflow: LAST STEP → visual verification | USE → AI preview

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

    Workflow: BEFORE → operations | AFTER → scene_compare_snapshot

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

    Workflow: AFTER → scene_snapshot_state (x2) | USE → verify changes

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

# Internal function - exposed via scene_inspect mega tool
def _scene_inspect_material_slots(
    ctx: Context,
    material_filter: Optional[str] = None,
    include_empty_slots: bool = True
) -> str:
    """
    [SCENE][SAFE][READ-ONLY] Audits material slot assignments across the entire scene.

    Workflow: READ-ONLY | USE WITH → material_list_by_object

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

# Internal function - exposed via scene_inspect mega tool
def _scene_inspect_mesh_topology(
    ctx: Context,
    object_name: str,
    detailed: bool = False
) -> str:
    """
    [MESH][SAFE][READ-ONLY] Reports detailed topology stats for a given mesh.

    Workflow: READ-ONLY | USE → quality check before export

    Includes counts for vertices, edges, faces, triangles, quads, ngons.
    If detailed=True, checks for non-manifold edges and loose geometry (more expensive).

    Args:
        object_name: Name of the mesh object.
        detailed: If True, performs expensive checks (non-manifold, loose geometry).
    """
    handler = get_scene_handler()
    try:
        stats = handler.inspect_mesh_topology(object_name, detailed)
        import json
        
        lines = [
            f"Topology Report for '{stats.get('object_name')}':",
            f"- Vertices: {stats.get('vertex_count')}",
            f"- Edges: {stats.get('edge_count')}",
            f"- Faces: {stats.get('face_count')}",
            f"  - Triangles: {stats.get('triangle_count')}",
            f"  - Quads: {stats.get('quad_count')}",
            f"  - N-Gons: {stats.get('ngon_count')}",
        ]
        
        if detailed:
            lines.append("Detailed Checks:")
            lines.append(f"  - Non-Manifold Edges: {stats.get('non_manifold_edges')}")
            lines.append(f"  - Loose Vertices: {stats.get('loose_vertices')}")
            lines.append(f"  - Loose Edges: {stats.get('loose_edges')}")
            
        return "\n".join(lines)
    except RuntimeError as e:
        return str(e)
    
# Internal function - exposed via scene_inspect mega tool
def _scene_inspect_modifiers(
    ctx: Context,
    object_name: Optional[str] = None,
    include_disabled: bool = True
) -> str:
    """
    [SCENE][SAFE][READ-ONLY] Lists modifier stacks with key settings.

    Workflow: READ-ONLY | BEFORE → modeling_apply_modifier

    Can inspect a specific object or audit the entire scene.

    Args:
        object_name: Optional name of the object to inspect. If None, scans all objects.
        include_disabled: If True, includes modifiers disabled in viewport/render.
    """
    handler = get_scene_handler()
    try:
        result = handler.inspect_modifiers(object_name, include_disabled)
        import json
        
        obj_count = result.get("object_count", 0)
        mod_count = result.get("modifier_count", 0)
        objects = result.get("objects", [])
        
        if obj_count == 0:
            if object_name:
                return f"Object '{object_name}' has no modifiers."
            return "No modifiers found in the scene."
            
        lines = [
            f"Modifier Inspection ({mod_count} modifiers on {obj_count} objects):",
            ""
        ]
        
        # Limit output if scene-wide and too many objects
        limit = 20
        
        for i, obj in enumerate(objects):
            if i >= limit:
                lines.append(f"... and {len(objects) - limit} more objects")
                break
                
            lines.append(f"Object: {obj['name']}")
            for mod in obj['modifiers']:
                name = mod['name']
                mtype = mod['type']
                flags = []
                if not mod['show_viewport']:
                    flags.append("hidden_viewport")
                if not mod['show_render']:
                    flags.append("hidden_render")
                
                flag_str = f" [{', '.join(flags)}]" if flags else ""
                
                # Build details string from extra keys
                details = []
                for k, v in mod.items():
                    if k not in ["name", "type", "is_enabled", "show_viewport", "show_render"]:
                        details.append(f"{k}={v}")
                
                detail_str = f" ({', '.join(details)})" if details else ""
                
                lines.append(f"  - {name} ({mtype}){detail_str}{flag_str}")
            lines.append("")
            
        ctx.info(f"Inspected modifiers: {mod_count} on {obj_count} objects")
        return "\n".join(lines)
    except RuntimeError as e:
        return str(e)
        
        
@mcp.tool()
def scene_create(
    ctx: Context,
    action: Literal["light", "camera", "empty"],
    location: Union[str, List[float]] = [0.0, 0.0, 0.0],
    rotation: Union[str, List[float]] = [0.0, 0.0, 0.0],
    name: Optional[str] = None,
    # Light params:
    light_type: Literal["POINT", "SUN", "SPOT", "AREA"] = "POINT",
    energy: float = 1000.0,
    color: Union[str, List[float]] = [1.0, 1.0, 1.0],
    # Camera params:
    lens: float = 50.0,
    clip_start: Optional[float] = None,
    clip_end: Optional[float] = None,
    # Empty params:
    empty_type: Literal["PLAIN_AXES", "ARROWS", "SINGLE_ARROW", "CIRCLE", "CUBE", "SPHERE", "CONE", "IMAGE"] = "PLAIN_AXES",
    size: float = 1.0
) -> str:
    """
    [SCENE][SAFE] Creates scene helper objects (lights, cameras, empties).

    Actions and parameters:
    - "light": Creates light source. Optional: light_type (POINT/SUN/SPOT/AREA), energy, color, location, name.
    - "camera": Creates camera. Optional: location, rotation, lens, clip_start, clip_end, name.
    - "empty": Creates empty object. Optional: empty_type (PLAIN_AXES/ARROWS/CIRCLE/CUBE/SPHERE/CONE/IMAGE), size, location, name.

    All location/rotation/color params accept either list [x,y,z] or string "[x,y,z]".

    For mesh primitives (Cube, Sphere, etc.) use modeling_create_primitive instead.

    Workflow: AFTER → geometry complete | BEFORE → scene_get_viewport

    Examples:
        scene_create(action="light", light_type="SUN", energy=5.0)
        scene_create(action="light", light_type="AREA", location=[0, 0, 5], color=[1.0, 0.9, 0.8])
        scene_create(action="camera", location=[0, -10, 5], rotation=[1.0, 0, 0])
        scene_create(action="empty", empty_type="ARROWS", location=[0, 0, 2])
    """
    if action == "light":
        return _scene_create_light(ctx, light_type, energy, color, location, name)
    elif action == "camera":
        return _scene_create_camera(ctx, location, rotation, lens, clip_start, clip_end, name)
    elif action == "empty":
        return _scene_create_empty(ctx, empty_type, size, location, name)
    else:
        return f"Unknown action '{action}'. Valid actions: light, camera, empty"


# Internal function - exposed via scene_create mega tool
def _scene_create_light(
    ctx: Context,
    type: str,
    energy: float = 1000.0,
    color: Union[str, List[float]] = [1.0, 1.0, 1.0],
    location: Union[str, List[float]] = [0.0, 0.0, 5.0],
    name: Optional[str] = None
) -> str:
    """
    [SCENE][SAFE] Creates a light source.

    Workflow: AFTER → geometry complete | BEFORE → scene_get_viewport

    Args:
        type: 'POINT', 'SUN', 'SPOT', 'AREA'.
        energy: Power in Watts.
        color: [r, g, b] (0.0 to 1.0). Can be a list or string '[1.0, 1.0, 1.0]'.
        location: [x, y, z]. Can be a list or string.
        name: Optional custom name.
    """
    handler = get_scene_handler()
    try:
        parsed_color = parse_coordinate(color) or [1.0, 1.0, 1.0]
        parsed_location = parse_coordinate(location) or [0.0, 0.0, 5.0]
        return handler.create_light(type, energy, parsed_color, parsed_location, name)
    except (RuntimeError, ValueError) as e:
        return str(e)


# Internal function - exposed via scene_create mega tool
def _scene_create_camera(
    ctx: Context,
    location: Union[str, List[float]],
    rotation: Union[str, List[float]],
    lens: float = 50.0,
    clip_start: Optional[float] = None,
    clip_end: Optional[float] = None,
    name: Optional[str] = None
) -> str:
    """
    [SCENE][SAFE] Creates a camera object.

    Workflow: AFTER → geometry complete | USE WITH → scene_get_viewport

    Args:
        location: [x, y, z]. Can be a list or string '[0.0, 0.0, 10.0]'.
        rotation: [x, y, z] Euler angles in radians. Can be a list or string.
        lens: Focal length in mm.
        clip_start: Near clipping distance.
        clip_end: Far clipping distance.
        name: Optional custom name.
    """
    handler = get_scene_handler()
    try:
        parsed_location = parse_coordinate(location)
        parsed_rotation = parse_coordinate(rotation)
        return handler.create_camera(parsed_location, parsed_rotation, lens, clip_start, clip_end, name)
    except (RuntimeError, ValueError) as e:
        return str(e)


# Internal function - exposed via scene_create mega tool
def _scene_create_empty(
    ctx: Context,
    type: str,
    size: float = 1.0,
    location: Union[str, List[float]] = [0.0, 0.0, 0.0],
    name: Optional[str] = None
) -> str:
    """
    [SCENE][SAFE] Creates an Empty object (useful for grouping or tracking).

    Workflow: USE FOR → grouping/parenting | WITH → scene_set_active

    Args:
        type: 'PLAIN_AXES', 'ARROWS', 'SINGLE_ARROW', 'CIRCLE', 'CUBE', 'SPHERE', 'CONE', 'IMAGE'.
        size: Display size.
        location: [x, y, z]. Can be a list or string '[0.0, 0.0, 0.0]'.
        name: Optional custom name.
    """
    handler = get_scene_handler()
    try:
        parsed_location = parse_coordinate(location) or [0.0, 0.0, 0.0]
        return handler.create_empty(type, size, parsed_location, name)
    except (RuntimeError, ValueError) as e:
        return str(e)

@mcp.tool()
def scene_set_mode(ctx: Context, mode: str) -> str:
    """
    [SCENE][SAFE] Sets the interaction mode (OBJECT, EDIT, SCULPT, POSE, WEIGHT_PAINT, TEXTURE_PAINT).

    Workflow: CRITICAL → switching OBJECT↔EDIT | BEFORE → mesh_* or modeling_*

    Args:
        mode: The target mode (case-insensitive).
    """
    handler = get_scene_handler()
    try:
        return handler.set_mode(mode)
    except ValueError as e:
        return f"Validation error: {str(e)}"
    except RuntimeError as e:
        return str(e)