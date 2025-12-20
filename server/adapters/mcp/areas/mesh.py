from typing import List, Literal, Optional, Union
from fastmcp import Context
from server.adapters.mcp.instance import mcp
from server.adapters.mcp.context_utils import ctx_info
from server.adapters.mcp.router_helper import route_tool_call
from server.adapters.mcp.utils import parse_coordinate
from server.infrastructure.di import (
    get_mesh_handler,
    get_modeling_handler,
    get_scene_handler,
    get_uv_handler,
)


@mcp.tool()
def mesh_select(
    ctx: Context,
    action: Literal["all", "none", "linked", "more", "less", "boundary"],
    boundary_mode: Literal["EDGE", "VERT"] = "EDGE"
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Simple selection operations for mesh geometry.

    Actions:
    - "all": Selects all geometry. No params required.
    - "none": Deselects all geometry. No params required.
    - "linked": Selects all geometry connected to current selection.
    - "more": Grows selection by 1 step.
    - "less": Shrinks selection by 1 step.
    - "boundary": Selects boundary edges/vertices. Optional: boundary_mode (EDGE/VERT).

    Workflow: BEFORE → mesh_extrude, mesh_delete, mesh_boolean | START → new selection workflow

    Examples:
        mesh_select(action="all")
        mesh_select(action="none")
        mesh_select(action="linked")
        mesh_select(action="boundary", boundary_mode="EDGE")
    """
    def execute():
        if action == "all":
            return _mesh_select_all(ctx, deselect=False)
        elif action == "none":
            return _mesh_select_all(ctx, deselect=True)
        elif action == "linked":
            return _mesh_select_linked(ctx)
        elif action == "more":
            return _mesh_select_more(ctx)
        elif action == "less":
            return _mesh_select_less(ctx)
        elif action == "boundary":
            return _mesh_select_boundary(ctx, mode=boundary_mode)
        else:
            return f"Unknown action '{action}'. Valid actions: all, none, linked, more, less, boundary"

    return route_tool_call(
        tool_name="mesh_select",
        params={"action": action, "boundary_mode": boundary_mode},
        direct_executor=execute
    )


@mcp.tool()
def mesh_select_targeted(
    ctx: Context,
    action: Literal["by_index", "loop", "ring", "by_location"],
    # by_index params:
    indices: Optional[List[int]] = None,
    element_type: Literal["VERT", "EDGE", "FACE"] = "VERT",
    selection_mode: Literal["SET", "ADD", "SUBTRACT"] = "SET",
    # loop/ring params:
    edge_index: Optional[int] = None,
    # by_location params:
    axis: Optional[Literal["X", "Y", "Z"]] = None,
    min_coord: Optional[float] = None,
    max_coord: Optional[float] = None
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Targeted selection operations for mesh geometry.

    Actions and required parameters:
    - "by_index": Requires indices (list of ints). Optional: element_type (VERT/EDGE/FACE), selection_mode (SET/ADD/SUBTRACT).
    - "loop": Requires edge_index (int). Selects edge loop starting from that edge.
    - "ring": Requires edge_index (int). Selects edge ring starting from that edge.
    - "by_location": Requires axis (X/Y/Z), min_coord, max_coord. Optional: element_type. Selects geometry within coordinate range.

    Workflow: BEFORE → mesh_get_vertex_data (for indices) | AFTER → mesh_extrude, mesh_delete, mesh_boolean

    Examples:
        mesh_select_targeted(action="by_index", indices=[0, 1, 2], element_type="VERT")
        mesh_select_targeted(action="by_index", indices=[0, 1], element_type="FACE", selection_mode="ADD")
        mesh_select_targeted(action="loop", edge_index=4)
        mesh_select_targeted(action="ring", edge_index=3)
        mesh_select_targeted(action="by_location", axis="Z", min_coord=0.5, max_coord=2.0)
        mesh_select_targeted(action="by_location", axis="X", min_coord=-1.0, max_coord=0.0, element_type="FACE")
    """
    def execute():
        if action == "by_index":
            if indices is None:
                return "Error: 'by_index' action requires 'indices' parameter (list of integers)."
            return _mesh_select_by_index(ctx, indices, element_type, selection_mode)
        elif action == "loop":
            if edge_index is None:
                return "Error: 'loop' action requires 'edge_index' parameter (integer)."
            return _mesh_select_loop(ctx, edge_index)
        elif action == "ring":
            if edge_index is None:
                return "Error: 'ring' action requires 'edge_index' parameter (integer)."
            return _mesh_select_ring(ctx, edge_index)
        elif action == "by_location":
            if axis is None or min_coord is None or max_coord is None:
                return "Error: 'by_location' action requires 'axis', 'min_coord', and 'max_coord' parameters."
            return _mesh_select_by_location(ctx, axis, min_coord, max_coord, element_type)
        else:
            return f"Unknown action '{action}'. Valid actions: by_index, loop, ring, by_location"

    return route_tool_call(
        tool_name="mesh_select_targeted",
        params={
            "action": action,
            "indices": indices,
            "element_type": element_type,
            "selection_mode": selection_mode,
            "edge_index": edge_index,
            "axis": axis,
            "min_coord": min_coord,
            "max_coord": max_coord
        },
        direct_executor=execute
    )


# Internal function - exposed via mesh_select mega tool
def _mesh_select_all(ctx: Context, deselect: bool = False) -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Selects or deselects all geometry elements.

    Workflow: START → new workflow | AFTER → mesh_select_by_index, mesh_select_by_location

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

    Workflow: BEFORE → mesh_select_* | AFTER → mesh_merge_by_distance

    Args:
        type: 'VERT', 'EDGE', 'FACE'.
    """
    return route_tool_call(
        tool_name="mesh_delete_selected",
        params={"type": type},
        direct_executor=lambda: get_mesh_handler().delete_selected(type)
    )

# Internal function - exposed via mesh_select_targeted mega tool
def _mesh_select_by_index(ctx: Context, indices: List[int], type: str = 'VERT', selection_mode: str = 'SET') -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Selects specific geometry elements by index.
    Uses BMesh for precise 0-based indexing.

    Workflow: BEFORE → mesh_get_vertex_data | AFTER → mesh_select_linked, mesh_select_more

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
def mesh_extrude_region(ctx: Context, move: Union[str, List[float], None] = None) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Extrudes selected geometry.
    WARNING: If 'move' is None, new geometry is created in-place (overlapping).
    Always provide 'move' vector or follow up with transform.

    Workflow: BEFORE → mesh_select_* | AFTER → mesh_smooth, mesh_merge_by_distance

    Args:
        move: Optional [x, y, z] vector to move extruded region. Can be a list or string '[0.0, 0.0, 2.0]'.
    """
    def execute():
        try:
            parsed_move = parse_coordinate(move)
            return get_mesh_handler().extrude_region(parsed_move)
        except (RuntimeError, ValueError) as e:
            return str(e)

    return route_tool_call(
        tool_name="mesh_extrude_region",
        params={"move": move},
        direct_executor=execute
    )

@mcp.tool()
def mesh_fill_holes(ctx: Context) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Fills holes by creating faces from selected edges/vertices.
    Equivalent to pressing 'F' key in Blender.

    Workflow: BEFORE → mesh_select_boundary (CRITICAL!) | AFTER → mesh_merge_by_distance
    """
    return route_tool_call(
        tool_name="mesh_fill_holes",
        params={},
        direct_executor=lambda: get_mesh_handler().fill_holes()
    )

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

    Workflow: BEFORE → mesh_select_loop, mesh_select_ring | AFTER → mesh_smooth

    Args:
        offset: Size of the bevel (distance/width).
        segments: Number of segments (rounding).
        profile: Shape of the bevel (0.5 is round).
        affect: 'EDGES' or 'VERTICES'.
    """
    return route_tool_call(
        tool_name="mesh_bevel",
        params={"offset": offset, "segments": segments, "profile": profile, "affect": affect},
        direct_executor=lambda: get_mesh_handler().bevel(offset, segments, profile, affect)
    )

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

    Workflow: BEFORE → mesh_select_by_index(EDGE) | AFTER → mesh_select_loop

    Args:
        number_cuts: Number of cuts to make.
        smoothness: Smoothness of the subdivision.
    """
    return route_tool_call(
        tool_name="mesh_loop_cut",
        params={"number_cuts": number_cuts, "smoothness": smoothness},
        direct_executor=lambda: get_mesh_handler().loop_cut(number_cuts, smoothness)
    )

@mcp.tool()
def mesh_inset(
    ctx: Context,
    thickness: float = 0.0,
    depth: float = 0.0
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Insets selected faces (creates smaller faces inside).

    Workflow: BEFORE → mesh_select_*(FACE) | AFTER → mesh_extrude_region

    Args:
        thickness: Amount to inset.
        depth: Amount to move the inset face in/out.
    """
    return route_tool_call(
        tool_name="mesh_inset",
        params={"thickness": thickness, "depth": depth},
        direct_executor=lambda: get_mesh_handler().inset(thickness, depth)
    )

@mcp.tool()
def mesh_boolean(
    ctx: Context,
    operation: str = 'DIFFERENCE',
    solver: str = 'EXACT'
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Boolean operation on selected geometry.
    Formula: Unselected - Selected (for DIFFERENCE).
    TIP: For object-level booleans, prefer 'modeling_add_modifier(BOOLEAN)' (safer).

    Workflow: BEFORE → modeling_join_objects + mesh_select_linked | AFTER → mesh_merge_by_distance, mesh_fill_holes

    Workflow:
      1. Select 'Cutter' geometry.
      2. Deselect 'Base' geometry.
      3. Run tool.

    Args:
        operation: 'INTERSECT', 'UNION', 'DIFFERENCE'.
        solver: 'EXACT' (modern, recommended) or 'FLOAT' (legacy).
    """
    return route_tool_call(
        tool_name="mesh_boolean",
        params={"operation": operation, "solver": solver},
        direct_executor=lambda: get_mesh_handler().boolean(operation, solver)
    )

@mcp.tool()
def mesh_merge_by_distance(
    ctx: Context,
    distance: float = 0.001
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Merges vertices within threshold distance.
    Useful for cleaning up geometry after imports or boolean ops.

    Workflow: BEFORE → mesh_boolean, mesh_extrude | AFTER → mesh_smooth

    Args:
        distance: Threshold distance to merge.
    """
    return route_tool_call(
        tool_name="mesh_merge_by_distance",
        params={"distance": distance},
        direct_executor=lambda: get_mesh_handler().merge_by_distance(distance)
    )

@mcp.tool()
def mesh_subdivide(
    ctx: Context,
    number_cuts: int = 1,
    smoothness: float = 0.0
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Subdivides selected geometry.

    Workflow: BEFORE → mesh_select_* | AFTER → mesh_smooth

    Args:
        number_cuts: Number of cuts.
        smoothness: Smoothness factor (0.0 to 1.0).
    """
    return route_tool_call(
        tool_name="mesh_subdivide",
        params={"number_cuts": number_cuts, "smoothness": smoothness},
        direct_executor=lambda: get_mesh_handler().subdivide(number_cuts, smoothness)
    )

@mcp.tool()
def mesh_smooth(
    ctx: Context,
    iterations: int = 1,
    factor: float = 0.5
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE] Smooths selected vertices.
    Uses Laplacian smoothing to refine organic shapes and remove hard edges.

    Workflow: BEFORE → mesh_boolean, mesh_extrude, mesh_bevel | LAST STEP in edit workflow

    Args:
        iterations: Number of smoothing passes (1-100). More = smoother
        factor: Smoothing strength (0.0-1.0). 0=no effect, 1=maximum smoothing
    """
    return route_tool_call(
        tool_name="mesh_smooth",
        params={"iterations": iterations, "factor": factor},
        direct_executor=lambda: get_mesh_handler().smooth_vertices(iterations, factor)
    )

@mcp.tool()
def mesh_flatten(
    ctx: Context,
    axis: str
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Flattens selected vertices to plane.
    Aligns vertices perpendicular to chosen axis (X: YZ plane, Y: XZ plane, Z: XY plane).

    Workflow: BEFORE → mesh_select_by_location | USE FOR → creating flat surfaces

    Args:
        axis: Axis to flatten along ("X", "Y", or "Z")
    """
    return route_tool_call(
        tool_name="mesh_flatten",
        params={"axis": axis},
        direct_executor=lambda: get_mesh_handler().flatten_vertices(axis)
    )
    
    
@mcp.tool()
def mesh_list_groups(
    ctx: Context,
    object_name: str,
    group_type: str = 'VERTEX'
) -> str:
    """
    [MESH][SAFE][READ-ONLY] Lists vertex/face groups defined on mesh.

    Workflow: READ-ONLY | USE WITH → scene_inspect_object

    Args:
        object_name: Name of the mesh object.
        group_type: 'VERTEX' or 'FACE' (defaults to VERTEX).
    """
    def execute():
        handler = get_mesh_handler()
        try:
            result = handler.list_groups(object_name, group_type)

            obj_name = result.get("object_name")
            g_type = result.get("group_type")
            count = result.get("group_count", 0)
            groups = result.get("groups", [])
            note = result.get("note")

            if count == 0:
                msg = f"Object '{obj_name}' has no {g_type.lower()} groups."
                if note:
                    msg += f"\nNote: {note}"
                return msg

            lines = [
                f"Object: {obj_name}",
                f"{g_type} Groups ({count}):"
            ]

            # Limit output if too many groups
            limit = 50

            for i, group in enumerate(groups):
                if i >= limit:
                    lines.append(f"  ... and {len(groups) - limit} more")
                    break

                name = group.get("name")
                idx = group.get("index")
                # For vertex groups, show member count if available
                # For face maps/attrs, show type info

                extras = []
                if "member_count" in group:
                    extras.append(f"members: {group['member_count']}")
                if "lock_weight" in group and group["lock_weight"]:
                    extras.append("locked")
                if "data_type" in group:
                    extras.append(f"type: {group['data_type']}")

                extra_str = f" ({', '.join(extras)})" if extras else ""

                lines.append(f"  [{idx if idx is not None else '-'}] {name}{extra_str}")

            if note:
                lines.append(f"\nNote: {note}")

            ctx_info(ctx, f"Listed {count} {g_type} groups for '{obj_name}'")
            return "\n".join(lines)

        except RuntimeError as e:
            return str(e)

    return route_tool_call(
        tool_name="mesh_list_groups",
        params={"object_name": object_name, "group_type": group_type},
        direct_executor=execute
    )
# Internal function - exposed via mesh_select_targeted mega tool
def _mesh_select_loop(
    ctx: Context,
    edge_index: int
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Selects an edge loop based on the target edge index.

    Workflow: BEFORE → mesh_select_by_index(EDGE) | AFTER → mesh_bevel, mesh_extrude

    Edge loops are continuous lines of edges that form rings around the mesh topology.
    This is crucial for selecting borders, seams, or topological features.

    Args:
        edge_index: Index of the target edge that defines which loop to select.

    Returns:
        Success message indicating the loop was selected.

    Example:
        mesh_select_loop(edge_index=5) -> Selects the edge loop containing edge 5
    """
    handler = get_mesh_handler()
    try:
        return handler.select_loop(edge_index)
    except RuntimeError as e:
        return str(e)


# Internal function - exposed via mesh_select_targeted mega tool
def _mesh_select_ring(
    ctx: Context,
    edge_index: int
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Selects an edge ring based on the target edge index.

    Workflow: BEFORE → mesh_select_by_index(EDGE) | AFTER → mesh_loop_cut

    Edge rings are parallel rings of edges that run perpendicular to edge loops.
    Useful for selecting parallel topology features around cylindrical or circular structures.

    Args:
        edge_index: Index of the target edge that defines which ring to select.

    Returns:
        Success message indicating the ring was selected.

    Example:
        mesh_select_ring(edge_index=3) -> Selects the edge ring containing edge 3
    """
    handler = get_mesh_handler()
    try:
        return handler.select_ring(edge_index)
    except RuntimeError as e:
        return str(e)

# Internal function - exposed via mesh_select mega tool
def _mesh_select_linked(ctx: Context) -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Selects all geometry linked to current selection.

    Workflow: BEFORE → mesh_select_by_index (one vert) | CRITICAL FOR → mesh_boolean after join

    Selects all connected/linked geometry (mesh islands) starting from the current selection.
    This is CRITICAL for multi-part operations like booleans after joining objects.

    Use case: After joining two cubes, select one vertex of the first cube,
    then use mesh_select_linked to select the entire first cube island.

    Returns:
        Success message indicating linked geometry was selected.

    Example:
        mesh_select_linked() -> Selects all geometry connected to current selection
    """
    handler = get_mesh_handler()
    try:
        return handler.select_linked()
    except RuntimeError as e:
        return str(e)


# Internal function - exposed via mesh_select mega tool
def _mesh_select_more(ctx: Context) -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Grows the current selection by one step.

    Workflow: AFTER → mesh_select_* | USE → grow selection iteratively

    Expands the selection to include all geometry elements adjacent to the current selection.
    Useful for gradually expanding selection regions or creating selection borders.

    Returns:
        Success message indicating selection was expanded.

    Example:
        mesh_select_more() -> Expands selection by one step
    """
    handler = get_mesh_handler()
    try:
        return handler.select_more()
    except RuntimeError as e:
        return str(e)


# Internal function - exposed via mesh_select mega tool
def _mesh_select_less(ctx: Context) -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Shrinks the current selection by one step.

    Workflow: AFTER → mesh_select_* | USE → shrink selection from boundaries

    Contracts the selection by removing boundary elements from the current selection.
    Useful for refining selections or removing outer layers.

    Returns:
        Success message indicating selection was contracted.

    Example:
        mesh_select_less() -> Contracts selection by one step
    """
    handler = get_mesh_handler()
    try:
        return handler.select_less()
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_inspect(
    ctx: Context,
    action: Literal[
        "summary",
        "vertices",
        "edges",
        "faces",
        "uvs",
        "normals",
        "attributes",
        "shape_keys",
        "group_weights",
    ],
    object_name: Optional[str] = None,
    selected_only: bool = False,
    uv_layer: Optional[str] = None,
    attribute_name: Optional[str] = None,
    group_name: Optional[str] = None,
    include_deltas: bool = False,
) -> str:
    """
    [MESH][READ-ONLY][SAFE] Mega tool for mesh introspection.

    Actions and required parameters:
    - "summary": Requires object_name. Returns counts + flags only.
    - "vertices": Requires object_name. Returns vertex positions.
    - "edges": Requires object_name. Returns edge connectivity.
    - "faces": Requires object_name. Returns face connectivity.
    - "uvs": Requires object_name. Returns UV loop data.
    - "normals": Requires object_name. Returns per-loop normals.
    - "attributes": Requires object_name. Returns mesh attributes.
    - "shape_keys": Requires object_name. Returns shape key data.
    - "group_weights": Requires object_name. Returns vertex group weights.

    Action → parameter hints:
    - "summary": ignores selected_only, uv_layer, attribute_name, group_name, include_deltas
    - "vertices"/"edges"/"faces"/"normals": selected_only applies
    - "uvs": uv_layer (optional) + selected_only
    - "attributes": attribute_name (optional) + selected_only
    - "shape_keys": include_deltas (optional)
    - "group_weights": group_name (optional) + selected_only

    Workflow: READ-ONLY | USE → mesh reconstruction and quick audits

    Examples:
        mesh_inspect(action="summary", object_name="Cube")
        mesh_inspect(action="vertices", object_name="Cube", selected_only=True)
        mesh_inspect(action="uvs", object_name="Cube", uv_layer="UVMap")
        mesh_inspect(action="shape_keys", object_name="Face", include_deltas=True)
    """
    def execute():
        if object_name is None:
            return f"Error: '{action}' action requires 'object_name' parameter."

        if action == "summary":
            return _mesh_inspect_summary(ctx, object_name)
        elif action == "vertices":
            return _mesh_get_vertex_data(ctx, object_name, selected_only)
        elif action == "edges":
            return _mesh_get_edge_data(ctx, object_name, selected_only)
        elif action == "faces":
            return _mesh_get_face_data(ctx, object_name, selected_only)
        elif action == "uvs":
            return _mesh_get_uv_data(ctx, object_name, uv_layer, selected_only)
        elif action == "normals":
            return _mesh_get_loop_normals(ctx, object_name, selected_only)
        elif action == "attributes":
            return _mesh_get_attributes(ctx, object_name, attribute_name, selected_only)
        elif action == "shape_keys":
            return _mesh_get_shape_keys(ctx, object_name, include_deltas)
        elif action == "group_weights":
            return _mesh_get_vertex_group_weights(ctx, object_name, group_name, selected_only)
        else:
            return (
                f"Unknown action '{action}'. Valid actions: summary, vertices, edges, "
                "faces, uvs, normals, attributes, shape_keys, group_weights"
            )

    return route_tool_call(
        tool_name="mesh_inspect",
        params={
            "action": action,
            "object_name": object_name,
            "selected_only": selected_only,
            "uv_layer": uv_layer,
            "attribute_name": attribute_name,
            "group_name": group_name,
            "include_deltas": include_deltas,
        },
        direct_executor=execute
    )


# Internal function - exposed via mesh_inspect mega tool
def _mesh_get_vertex_data(
    ctx: Context,
    object_name: str,
    selected_only: bool = False
) -> str:
    """
    [EDIT MODE][READ-ONLY][SAFE] Returns vertex positions and selection states for programmatic analysis.
    """
    try:
        import json
        result = get_mesh_handler().get_vertex_data(object_name, selected_only)
        return json.dumps(result, indent=2)
    except RuntimeError as e:
        return str(e)


# Internal function - exposed via mesh_inspect mega tool
def _mesh_get_edge_data(
    ctx: Context,
    object_name: str,
    selected_only: bool = False
) -> str:
    """
    [EDIT MODE][READ-ONLY][SAFE] Returns edge connectivity + attributes.
    """
    try:
        import json
        result = get_mesh_handler().get_edge_data(object_name, selected_only)
        return json.dumps(result, indent=2)
    except RuntimeError as e:
        return str(e)


# Internal function - exposed via mesh_inspect mega tool
def _mesh_get_face_data(
    ctx: Context,
    object_name: str,
    selected_only: bool = False
) -> str:
    """
    [EDIT MODE][READ-ONLY][SAFE] Returns face connectivity + attributes.
    """
    try:
        import json
        result = get_mesh_handler().get_face_data(object_name, selected_only)
        return json.dumps(result, indent=2)
    except RuntimeError as e:
        return str(e)


# Internal function - exposed via mesh_inspect mega tool
def _mesh_get_uv_data(
    ctx: Context,
    object_name: str,
    uv_layer: Optional[str] = None,
    selected_only: bool = False
) -> str:
    """
    [EDIT MODE][READ-ONLY][SAFE] Returns UVs per face loop.
    """
    try:
        import json
        result = get_mesh_handler().get_uv_data(object_name, uv_layer, selected_only)
        return json.dumps(result, indent=2)
    except RuntimeError as e:
        return str(e)


# Internal function - exposed via mesh_inspect mega tool
def _mesh_get_loop_normals(
    ctx: Context,
    object_name: str,
    selected_only: bool = False
) -> str:
    """
    [EDIT MODE][READ-ONLY][SAFE] Returns per-loop normals (split/custom).
    """
    try:
        import json
        result = get_mesh_handler().get_loop_normals(object_name, selected_only)
        return json.dumps(result, indent=2)
    except RuntimeError as e:
        return str(e)


# Internal function - exposed via mesh_inspect mega tool
def _mesh_get_vertex_group_weights(
    ctx: Context,
    object_name: str,
    group_name: Optional[str] = None,
    selected_only: bool = False
) -> str:
    """
    [EDIT MODE][READ-ONLY][SAFE] Returns vertex group weights.
    """
    try:
        import json
        result = get_mesh_handler().get_vertex_group_weights(
            object_name,
            group_name,
            selected_only
        )
        return json.dumps(result, indent=2)
    except RuntimeError as e:
        return str(e)


# Internal function - exposed via mesh_inspect mega tool
def _mesh_get_attributes(
    ctx: Context,
    object_name: str,
    attribute_name: Optional[str] = None,
    selected_only: bool = False
) -> str:
    """
    [EDIT MODE][READ-ONLY][SAFE] Returns mesh attribute data (vertex colors, layers).
    """
    try:
        import json
        result = get_mesh_handler().get_attributes(
            object_name,
            attribute_name,
            selected_only
        )
        return json.dumps(result, indent=2)
    except RuntimeError as e:
        return str(e)


# Internal function - exposed via mesh_inspect mega tool
def _mesh_get_shape_keys(
    ctx: Context,
    object_name: str,
    include_deltas: bool = False
) -> str:
    """
    [OBJECT MODE][READ-ONLY][SAFE] Returns shape key data.
    """
    try:
        import json
        result = get_mesh_handler().get_shape_keys(object_name, include_deltas)
        return json.dumps(result, indent=2)
    except RuntimeError as e:
        return str(e)


# Internal function - exposed via mesh_inspect mega tool
def _mesh_inspect_summary(ctx: Context, object_name: str) -> str:
    """
    [MESH][READ-ONLY][SAFE] Returns a lightweight overview for quick audits.
    """
    try:
        import json

        topology = get_scene_handler().inspect_mesh_topology(object_name, detailed=False)
        uv_maps = get_uv_handler().list_maps(object_name, include_island_counts=False)
        shape_keys = get_mesh_handler().get_shape_keys(object_name, include_deltas=False)
        normals = get_mesh_handler().get_loop_normals(object_name, selected_only=False)
        groups = get_mesh_handler().list_groups(object_name, group_type="VERTEX")
        modifiers = get_modeling_handler().get_modifiers(object_name)

        summary = {
            "object_name": object_name,
            "vertex_count": topology.get("vertex_count"),
            "edge_count": topology.get("edge_count"),
            "face_count": topology.get("face_count"),
            "has_uvs": bool(uv_maps.get("uv_map_count", 0)),
            "has_shape_keys": bool(shape_keys.get("shape_key_count", 0)),
            "has_custom_normals": bool(normals.get("custom_normals", False)),
            "vertex_groups": [
                group.get("name")
                for group in (groups.get("groups") or [])
                if isinstance(group, dict) and group.get("name")
            ],
            "modifiers": [
                modifier.get("name")
                for modifier in (modifiers or [])
                if isinstance(modifier, dict) and modifier.get("name")
            ],
        }

        return json.dumps(summary, indent=2)
    except RuntimeError as e:
        return str(e)

# Internal function - exposed via mesh_select_targeted mega tool
def _mesh_select_by_location(
    ctx: Context,
    axis: str,
    min_coord: float,
    max_coord: float,
    mode: str = 'VERT'
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Selects geometry within coordinate range on specified axis.

    Workflow: BEFORE → mesh_get_vertex_data (optional) | AFTER → mesh_select_more, mesh_select_linked

    Enables spatial selection without manual index specification. Selects all vertices/edges/faces
    whose coordinates fall within the specified range on the given axis.

    Args:
        axis: 'X', 'Y', or 'Z' - the axis to evaluate
        min_coord: Minimum coordinate value (inclusive)
        max_coord: Maximum coordinate value (inclusive)
        mode: 'VERT' (vertices), 'EDGE' (edges), or 'FACE' (faces) - what to select

    Returns:
        Success message with count of selected elements.

    Use cases:
        - "Select all vertices above Z=0.5" -> axis='Z', min_coord=0.5, max_coord=999
        - "Select faces in middle section" -> axis='Y', min_coord=-0.5, max_coord=0.5
        - "Select left half of mesh" -> axis='X', min_coord=-999, max_coord=0

    Examples:
        mesh_select_by_location(axis='Z', min_coord=0.5, max_coord=10.0)
          -> Selects all vertices with Z >= 0.5

        mesh_select_by_location(axis='Y', min_coord=-1.0, max_coord=1.0, mode='FACE')
          -> Selects all faces with centroids between Y=-1 and Y=1
    """
    handler = get_mesh_handler()
    try:
        return handler.select_by_location(axis, min_coord, max_coord, mode)
    except RuntimeError as e:
        return str(e)

# Internal function - exposed via mesh_select mega tool
def _mesh_select_boundary(
    ctx: Context,
    mode: str = 'EDGE'
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Selects boundary edges or vertices (🔴 CRITICAL for mesh_fill_holes).

    Workflow: CRITICAL BEFORE → mesh_fill_holes | USE → find holes/open edges

    Boundary edges have only ONE adjacent face (indicating a hole or open edge in the mesh).
    Boundary vertices are connected to boundary edges.

    This is CRITICAL for mesh_fill_holes - use this to select specific hole edges before filling,
    instead of selecting everything with mesh_select_all.

    Args:
        mode: 'EDGE' (select boundary edges) or 'VERT' (select boundary vertices)

    Returns:
        Success message with count of boundary elements selected.

    Use cases:
        - Select edges of a specific hole before mesh_fill_holes
        - Identify open edges in mesh for quality checks
        - Select boundary loops for extrusion/detachment operations

    Workflow for targeted hole filling:
        1. mesh_select_boundary(mode='EDGE')  # Select all hole edges
        2. mesh_select_by_index to refine to specific hole (optional)
        3. mesh_fill_holes()  # Fill only the selected hole

    Examples:
        mesh_select_boundary(mode='EDGE') -> Selects all edges with only 1 face
        mesh_select_boundary(mode='VERT') -> Selects all vertices on boundaries
    """
    handler = get_mesh_handler()
    try:
        return handler.select_boundary(mode)
    except RuntimeError as e:
        return str(e)


# ==============================================================================
# TASK-016: Organic & Deform Tools
# ==============================================================================

@mcp.tool()
def mesh_randomize(
    ctx: Context,
    amount: float = 0.1,
    uniform: float = 0.0,
    normal: float = 0.0,
    seed: int = 0
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Randomizes vertex positions.
    Useful for making organic surfaces less perfect and adding natural variation.

    Workflow: BEFORE → mesh_select_* | AFTER → mesh_smooth (optional)

    Args:
        amount: Maximum displacement amount (default 0.1)
        uniform: Uniform random displacement (0.0-1.0). Displaces equally in all directions.
        normal: Normal-based displacement (0.0-1.0). Displaces along vertex normals.
        seed: Random seed for reproducible results (0 = random)

    Examples:
        mesh_randomize(amount=0.05) -> Subtle surface noise
        mesh_randomize(amount=0.2, normal=1.0) -> Displacement along normals
        mesh_randomize(amount=0.1, uniform=0.5, normal=0.5, seed=42) -> Mix with fixed seed
    """
    return route_tool_call(
        tool_name="mesh_randomize",
        params={"amount": amount, "uniform": uniform, "normal": normal, "seed": seed},
        direct_executor=lambda: get_mesh_handler().randomize(amount, uniform, normal, seed)
    )


@mcp.tool()
def mesh_shrink_fatten(
    ctx: Context,
    value: float
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Moves vertices along their normals (Shrink/Fatten).
    Crucial for thickening or thinning organic shapes without losing volume style.
    Positive values = fatten (outward), negative values = shrink (inward).

    Workflow: BEFORE → mesh_select_* | AFTER → mesh_smooth (optional)

    Args:
        value: Distance to move along normals. Positive = outward, negative = inward.

    Examples:
        mesh_shrink_fatten(value=0.1) -> Fatten/inflate selected vertices
        mesh_shrink_fatten(value=-0.05) -> Shrink/deflate selected vertices
    """
    return route_tool_call(
        tool_name="mesh_shrink_fatten",
        params={"value": value},
        direct_executor=lambda: get_mesh_handler().shrink_fatten(value)
    )


# ==============================================================================
# TASK-017: Vertex Group Tools
# ==============================================================================

@mcp.tool()
def mesh_create_vertex_group(
    ctx: Context,
    object_name: str,
    name: str
) -> str:
    """
    [MESH][SAFE] Creates a new vertex group on the specified mesh object.
    Vertex groups are used for weight painting, armature deformation, and selective operations.

    Workflow: START → mesh_assign_to_group | USE WITH → mesh_list_groups

    Args:
        object_name: Name of the mesh object to add the group to
        name: Name for the new vertex group

    Examples:
        mesh_create_vertex_group(object_name="Body", name="Head")
        mesh_create_vertex_group(object_name="Character", name="LeftArm")
    """
    return route_tool_call(
        tool_name="mesh_create_vertex_group",
        params={"object_name": object_name, "name": name},
        direct_executor=lambda: get_mesh_handler().create_vertex_group(object_name, name)
    )


@mcp.tool()
def mesh_assign_to_group(
    ctx: Context,
    object_name: str,
    group_name: str,
    weight: float = 1.0
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Assigns selected vertices to a vertex group.
    Weight controls influence strength (0.0 = no influence, 1.0 = full influence).

    Workflow: BEFORE → mesh_select_*, mesh_create_vertex_group | USE WITH → mesh_list_groups

    Args:
        object_name: Name of the mesh object
        group_name: Name of the vertex group to assign to
        weight: Weight value for assignment (0.0 to 1.0, default 1.0)

    Examples:
        mesh_assign_to_group(object_name="Body", group_name="Head", weight=1.0)
        mesh_assign_to_group(object_name="Arm", group_name="Bicep", weight=0.5)
    """
    return route_tool_call(
        tool_name="mesh_assign_to_group",
        params={"object_name": object_name, "group_name": group_name, "weight": weight},
        direct_executor=lambda: get_mesh_handler().assign_to_group(object_name, group_name, weight)
    )


@mcp.tool()
def mesh_remove_from_group(
    ctx: Context,
    object_name: str,
    group_name: str
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Removes selected vertices from a vertex group.

    Workflow: BEFORE → mesh_select_* | USE WITH → mesh_list_groups, mesh_assign_to_group

    Args:
        object_name: Name of the mesh object
        group_name: Name of the vertex group to remove from

    Examples:
        mesh_remove_from_group(object_name="Body", group_name="Head")
    """
    return route_tool_call(
        tool_name="mesh_remove_from_group",
        params={"object_name": object_name, "group_name": group_name},
        direct_executor=lambda: get_mesh_handler().remove_from_group(object_name, group_name)
    )


# ==============================================================================
# TASK-018: Phase 2.5 - Advanced Precision Tools
# ==============================================================================

@mcp.tool()
def mesh_bisect(
    ctx: Context,
    plane_co: List[float],
    plane_no: List[float],
    clear_inner: bool = False,
    clear_outer: bool = False,
    fill: bool = False
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Cuts mesh along a plane.
    Can optionally remove geometry on either side and fill the cut with a face.

    Workflow: BEFORE → mesh_select_* | AFTER → mesh_fill_holes, mesh_merge_by_distance

    Args:
        plane_co: Point on the cutting plane [x, y, z]. E.g. [0, 0, 0] for origin.
        plane_no: Normal direction of the plane [x, y, z]. E.g. [0, 0, 1] for Z-up plane.
        clear_inner: If True, removes geometry on the negative side of the plane.
        clear_outer: If True, removes geometry on the positive side of the plane.
        fill: If True, fills the cut with a face (creates cap).

    Examples:
        mesh_bisect(plane_co=[0,0,0], plane_no=[0,0,1]) -> Cut at Z=0 (horizontal plane)
        mesh_bisect(plane_co=[0,0,1], plane_no=[0,0,1], clear_outer=True) -> Cut and remove top
        mesh_bisect(plane_co=[0,0,0], plane_no=[1,0,0], fill=True) -> Cut at X=0 with cap
    """
    return route_tool_call(
        tool_name="mesh_bisect",
        params={"plane_co": plane_co, "plane_no": plane_no, "clear_inner": clear_inner, "clear_outer": clear_outer, "fill": fill},
        direct_executor=lambda: get_mesh_handler().bisect(plane_co, plane_no, clear_inner, clear_outer, fill)
    )


@mcp.tool()
def mesh_edge_slide(
    ctx: Context,
    value: float = 0.0
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Slides selected edges along mesh topology.
    Maintains mesh connectivity while repositioning edge loops.
    Value range is -1.0 to 1.0 (relative to adjacent edges).

    Workflow: BEFORE → mesh_select_loop, mesh_select_ring | AFTER → mesh_smooth

    Args:
        value: Slide amount (-1.0 to 1.0). 0 = no movement. Negative = one direction, positive = other.

    Examples:
        mesh_edge_slide(value=0.5) -> Slide selected edges 50% toward one side
        mesh_edge_slide(value=-0.3) -> Slide selected edges 30% toward other side
    """
    return route_tool_call(
        tool_name="mesh_edge_slide",
        params={"value": value},
        direct_executor=lambda: get_mesh_handler().edge_slide(value)
    )


@mcp.tool()
def mesh_vert_slide(
    ctx: Context,
    value: float = 0.0
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Slides selected vertices along connected edges.
    Moves vertices along the edge they are connected to without changing topology.
    Value range is -1.0 to 1.0 (relative to connected edge length).

    Workflow: BEFORE → mesh_select_by_index(VERT) | AFTER → mesh_smooth

    Args:
        value: Slide amount (-1.0 to 1.0). 0 = no movement.

    Examples:
        mesh_vert_slide(value=0.5) -> Slide vertices 50% along their connected edges
        mesh_vert_slide(value=-0.2) -> Slide vertices 20% in opposite direction
    """
    return route_tool_call(
        tool_name="mesh_vert_slide",
        params={"value": value},
        direct_executor=lambda: get_mesh_handler().vert_slide(value)
    )


@mcp.tool()
def mesh_triangulate(ctx: Context) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Converts selected faces to triangles.
    Useful for export to game engines or ensuring consistent topology.
    NOTE: This is irreversible - consider using a TRIANGULATE modifier for non-destructive workflow.

    Workflow: BEFORE → mesh_select_*(FACE) | USE FOR → game export prep, boolean cleanup

    Examples:
        mesh_triangulate() -> Converts all selected faces to triangles
    """
    return route_tool_call(
        tool_name="mesh_triangulate",
        params={},
        direct_executor=lambda: get_mesh_handler().triangulate()
    )


@mcp.tool()
def mesh_remesh_voxel(
    ctx: Context,
    voxel_size: float = 0.1,
    adaptivity: float = 0.0
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Remeshes object using Voxel algorithm.
    Creates uniform topology - useful for sculpting or boolean cleanup.
    WARNING: Destroys all existing topology, UVs, and vertex groups!

    Workflow: AFTER → mesh_boolean, modeling_join_objects | USE FOR → sculpt prep, topology cleanup

    Args:
        voxel_size: Size of voxels (smaller = more detail, more polygons). Default 0.1.
        adaptivity: Reduces polygons in flat areas (0.0-1.0). 0 = uniform, 1 = maximum reduction.

    Examples:
        mesh_remesh_voxel(voxel_size=0.05) -> High detail remesh
        mesh_remesh_voxel(voxel_size=0.2, adaptivity=0.5) -> Lower detail with adaptive reduction
    """
    return route_tool_call(
        tool_name="mesh_remesh_voxel",
        params={"voxel_size": voxel_size, "adaptivity": adaptivity},
        direct_executor=lambda: get_mesh_handler().remesh_voxel(voxel_size, adaptivity)
    )


# ==============================================================================
# TASK-019: Phase 2.4 - Core Transform & Geometry
# ==============================================================================

@mcp.tool()
def mesh_transform_selected(
    ctx: Context,
    translate: Union[str, List[float], None] = None,
    rotate: Union[str, List[float], None] = None,
    scale: Union[str, List[float], None] = None,
    pivot: Literal["MEDIAN_POINT", "BOUNDING_BOX_CENTER", "CURSOR", "INDIVIDUAL_ORIGINS", "ACTIVE_ELEMENT"] = "MEDIAN_POINT"
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Transforms selected geometry (move/rotate/scale).
    CRITICAL: This is the primary tool for repositioning geometry after selection.

    Workflow: BEFORE → mesh_select_* | AFTER → mesh_merge_by_distance

    Args:
        translate: Translation vector [x, y, z]. Moves geometry. Accepts list or string "[x, y, z]".
        rotate: Rotation in radians [x, y, z]. Rotates around pivot. Accepts list or string "[x, y, z]".
        scale: Scale factors [x, y, z]. Scales from pivot. Accepts list or string "[x, y, z]".
        pivot: Pivot point for rotation/scale.
            - MEDIAN_POINT: Center of selection (default)
            - BOUNDING_BOX_CENTER: Center of bounding box
            - CURSOR: 3D cursor position
            - INDIVIDUAL_ORIGINS: Each element's own origin
            - ACTIVE_ELEMENT: Active element's position

    Examples:
        mesh_transform_selected(translate=[0, 0, 2]) -> Move up by 2 units
        mesh_transform_selected(rotate=[0, 0, 1.5708]) -> Rotate 90° around Z
        mesh_transform_selected(scale=[2, 2, 1]) -> Double size in X and Y
        mesh_transform_selected(translate=[1, 0, 0], pivot="CURSOR") -> Move relative to cursor
    """
    def execute():
        try:
            parsed_translate = parse_coordinate(translate)
            parsed_rotate = parse_coordinate(rotate)
            parsed_scale = parse_coordinate(scale)
            return get_mesh_handler().transform_selected(parsed_translate, parsed_rotate, parsed_scale, pivot)
        except (RuntimeError, ValueError) as e:
            return str(e)

    return route_tool_call(
        tool_name="mesh_transform_selected",
        params={"translate": translate, "rotate": rotate, "scale": scale, "pivot": pivot},
        direct_executor=execute
    )


@mcp.tool()
def mesh_bridge_edge_loops(
    ctx: Context,
    number_cuts: int = 0,
    interpolation: Literal["LINEAR", "PATH", "SURFACE"] = "LINEAR",
    smoothness: float = 0.0,
    twist: int = 0
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Bridges two edge loops with faces.
    Connects two separate edge loops/rings to create connecting geometry.

    Workflow: BEFORE → mesh_select_loop (select two loops) | AFTER → mesh_smooth, mesh_subdivide

    Args:
        number_cuts: Number of intermediate cuts (0 = direct bridge).
        interpolation: How to interpolate the bridge.
            - LINEAR: Straight connection
            - PATH: Follow edge flow
            - SURFACE: Smooth surface interpolation
        smoothness: Smoothness factor for interpolation (0.0-1.0).
        twist: Number of twist segments between loops.

    Examples:
        mesh_bridge_edge_loops() -> Simple direct bridge
        mesh_bridge_edge_loops(number_cuts=4) -> Bridge with 4 subdivisions
        mesh_bridge_edge_loops(interpolation="SURFACE", smoothness=1.0) -> Smooth curved bridge
        mesh_bridge_edge_loops(twist=1) -> Twisted bridge connection
    """
    return route_tool_call(
        tool_name="mesh_bridge_edge_loops",
        params={"number_cuts": number_cuts, "interpolation": interpolation, "smoothness": smoothness, "twist": twist},
        direct_executor=lambda: get_mesh_handler().bridge_edge_loops(number_cuts, interpolation, smoothness, twist)
    )


@mcp.tool()
def mesh_duplicate_selected(
    ctx: Context,
    translate: Optional[List[float]] = None
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Duplicates selected geometry within the same mesh.
    Creates a copy of selected elements. New geometry is automatically selected.

    Workflow: BEFORE → mesh_select_* | AFTER → mesh_transform_selected

    Args:
        translate: Optional [x, y, z] offset for duplicated geometry.
            If not provided, duplicate is created in-place (overlapping).

    Examples:
        mesh_duplicate_selected(translate=[2, 0, 0]) -> Duplicate and move 2 units on X
        mesh_duplicate_selected() -> Duplicate in-place (WARNING: overlapping geometry!)
    """
    return route_tool_call(
        tool_name="mesh_duplicate_selected",
        params={"translate": translate},
        direct_executor=lambda: get_mesh_handler().duplicate_selected(translate)
    )


# ==============================================================================
# TASK-021: Phase 2.6 - Curves & Procedural (Mesh-based tools)
# ==============================================================================

@mcp.tool()
def mesh_spin(
    ctx: Context,
    steps: int = 12,
    angle: float = 6.283185,
    axis: Literal["X", "Y", "Z"] = "Z",
    center: Optional[List[float]] = None,
    dupli: bool = False
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Spins/lathes selected geometry around an axis.
    Creates rotational geometry like vases, bowls, or circular patterns.

    Workflow: BEFORE → mesh_select_* (select profile) | AFTER → mesh_merge_by_distance

    Args:
        steps: Number of steps/segments for the spin (12 = 30° per step for full circle).
        angle: Total angle in radians (default 6.283185 = 360° = full circle).
            Common values: 3.14159 (180°), 1.5708 (90°)
        axis: Axis to spin around (X, Y, or Z).
        center: Optional [x, y, z] center point for spin. Default is 3D cursor.
        dupli: If True, duplicates geometry instead of extruding.

    Examples:
        mesh_spin(steps=32) -> Full 360° spin with 32 segments (smooth)
        mesh_spin(steps=16, angle=3.14159) -> 180° half-spin
        mesh_spin(axis="X", center=[0, 0, 0]) -> Spin around X at origin
        mesh_spin(dupli=True) -> Create radial pattern without connecting faces
    """
    return route_tool_call(
        tool_name="mesh_spin",
        params={"steps": steps, "angle": angle, "axis": axis, "center": center, "dupli": dupli},
        direct_executor=lambda: get_mesh_handler().spin(steps, angle, axis, center, dupli)
    )


@mcp.tool()
def mesh_screw(
    ctx: Context,
    steps: int = 12,
    turns: int = 1,
    axis: Literal["X", "Y", "Z"] = "Z",
    center: Optional[List[float]] = None,
    offset: float = 0.0
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Creates spiral/screw/helical geometry.
    Combines rotation with translation for spirals, threads, springs, or helixes.

    Workflow: BEFORE → mesh_select_* (select profile) | AFTER → mesh_merge_by_distance

    Args:
        steps: Number of steps per turn (more = smoother spiral).
        turns: Number of complete rotations.
        axis: Axis to screw around (X, Y, or Z).
        center: Optional [x, y, z] center point. Default is 3D cursor.
        offset: Distance to move along axis per turn (thread pitch).

    Examples:
        mesh_screw(steps=32, turns=3, offset=0.5) -> 3-turn spiral with 0.5 unit pitch
        mesh_screw(turns=1, offset=0) -> Same as spin (no translation)
        mesh_screw(steps=64, turns=5, offset=0.2) -> Fine-threaded screw
    """
    return route_tool_call(
        tool_name="mesh_screw",
        params={"steps": steps, "turns": turns, "axis": axis, "center": center, "offset": offset},
        direct_executor=lambda: get_mesh_handler().screw(steps, turns, axis, center, offset)
    )


@mcp.tool()
def mesh_add_vertex(
    ctx: Context,
    position: List[float]
) -> str:
    """
    [EDIT MODE][DESTRUCTIVE] Adds a single vertex at the specified position.
    Useful for creating geometry from scratch or adding connection points.

    Workflow: START → mesh_add_edge_face | USE FOR → manual geometry construction

    Args:
        position: [x, y, z] coordinates for the new vertex.

    Examples:
        mesh_add_vertex(position=[0, 0, 0]) -> Add vertex at origin
        mesh_add_vertex(position=[1.5, 2.0, 0.5]) -> Add vertex at specific location
    """
    return route_tool_call(
        tool_name="mesh_add_vertex",
        params={"position": position},
        direct_executor=lambda: get_mesh_handler().add_vertex(position)
    )


@mcp.tool()
def mesh_add_edge_face(ctx: Context) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Creates an edge or face from selected vertices.
    - 2 vertices selected → creates edge
    - 3+ vertices selected → creates face
    Equivalent to pressing 'F' key in Blender.

    Workflow: BEFORE → mesh_select_by_index, mesh_add_vertex | AFTER → mesh_fill_holes

    Examples:
        (select 2 verts) mesh_add_edge_face() -> Creates edge between them
        (select 3+ verts) mesh_add_edge_face() -> Creates face from vertices
    """
    return route_tool_call(
        tool_name="mesh_add_edge_face",
        params={},
        direct_executor=lambda: get_mesh_handler().add_edge_face()
    )


# ==============================================================================
# TASK-029: Edge Weights & Creases (Subdivision Control)
# ==============================================================================

@mcp.tool()
def mesh_edge_crease(
    ctx: Context,
    crease_value: float = 1.0
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE] Sets crease weight on selected edges.

    Crease controls how Subdivision Surface modifier affects edges:
    - 0.0 = fully smoothed (no crease effect)
    - 1.0 = fully sharp (edge remains sharp after subdivision)

    CRITICAL for hard-surface modeling: weapons, vehicles, devices, architectural details.
    Use to maintain sharp edges while still having smooth surfaces elsewhere.

    Workflow: BEFORE → mesh_select_targeted(action="loop") | AFTER → modeling_add_modifier(type="SUBSURF")

    Args:
        crease_value: Crease weight (0.0 to 1.0). 0.0 = smooth, 1.0 = fully sharp.

    Examples:
        mesh_edge_crease(crease_value=1.0) -> Make selected edges fully sharp
        mesh_edge_crease(crease_value=0.5) -> Partially sharp edges (softer bevel effect)
        mesh_edge_crease(crease_value=0.0) -> Remove crease (fully smoothed)
    """
    return route_tool_call(
        tool_name="mesh_edge_crease",
        params={"crease_value": crease_value},
        direct_executor=lambda: get_mesh_handler().edge_crease(crease_value)
    )


@mcp.tool()
def mesh_bevel_weight(
    ctx: Context,
    weight: float = 1.0
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE] Sets bevel weight on selected edges.

    When Bevel modifier uses "Weight" limit method, only edges with weight > 0 are beveled.
    This allows selective beveling without selecting edges manually each time.

    Perfect for: product design, hard-surface modeling, architectural details.

    Workflow: BEFORE → mesh_select_targeted(action="loop") | AFTER → modeling_add_modifier(type="BEVEL", limit_method="WEIGHT")

    Args:
        weight: Bevel weight (0.0 to 1.0). 0.0 = no bevel, 1.0 = full bevel effect.

    Examples:
        mesh_bevel_weight(weight=1.0) -> Full bevel effect on selected edges
        mesh_bevel_weight(weight=0.5) -> Half bevel effect (smaller bevel)
        mesh_bevel_weight(weight=0.0) -> Remove bevel weight (no beveling)
    """
    return route_tool_call(
        tool_name="mesh_bevel_weight",
        params={"weight": weight},
        direct_executor=lambda: get_mesh_handler().bevel_weight(weight)
    )


@mcp.tool()
def mesh_mark_sharp(
    ctx: Context,
    action: Literal["mark", "clear"] = "mark"
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE] Marks or clears sharp edges.

    Sharp edges affect:
    - Auto Smooth: Splits normals at sharp edges for flat shading
    - Edge Split modifier: Creates hard edges without geometry duplication
    - Normal display and shading calculations

    Use for: visual edge definition, smooth shading control, normal maps.

    Workflow: BEFORE → mesh_select_targeted(action="loop")

    Args:
        action: "mark" to mark edges as sharp, "clear" to remove sharp marking.

    Examples:
        mesh_mark_sharp(action="mark") -> Mark selected edges as sharp
        mesh_mark_sharp(action="clear") -> Clear sharp marking from selected edges
    """
    return route_tool_call(
        tool_name="mesh_mark_sharp",
        params={"action": action},
        direct_executor=lambda: get_mesh_handler().mark_sharp(action)
    )


# ==============================================================================
# TASK-030: Mesh Cleanup & Optimization
# ==============================================================================

@mcp.tool()
def mesh_dissolve(
    ctx: Context,
    dissolve_type: Literal["verts", "edges", "faces", "limited"] = "limited",
    angle_limit: float = 5.0,
    use_face_split: bool = False,
    use_boundary_tear: bool = False
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Dissolves geometry while preserving shape.

    Types:
    - verts: Dissolve selected vertices (merge surrounding faces)
    - edges: Dissolve selected edges (merge adjacent faces)
    - faces: Dissolve selected faces (remove while keeping boundary)
    - limited: Auto-dissolve edges below angle threshold (best for cleanup)

    ESSENTIAL for game dev: Removes unnecessary edge loops, cleans up booleans.

    Workflow: BEFORE → mesh_select(action="all") | Limited dissolve is best for cleanup

    Args:
        dissolve_type: Type of dissolve operation ("verts", "edges", "faces", "limited").
        angle_limit: Max angle between faces for limited dissolve (degrees). Default 5.0.
        use_face_split: Split off non-planar faces. Default False.
        use_boundary_tear: Split off boundary vertices. Default False.

    Examples:
        mesh_dissolve(dissolve_type="limited", angle_limit=5.0) -> Clean up flat areas
        mesh_dissolve(dissolve_type="verts") -> Dissolve selected vertices
        mesh_dissolve(dissolve_type="edges") -> Dissolve selected edges
    """
    return route_tool_call(
        tool_name="mesh_dissolve",
        params={"dissolve_type": dissolve_type, "angle_limit": angle_limit, "use_face_split": use_face_split, "use_boundary_tear": use_boundary_tear},
        direct_executor=lambda: get_mesh_handler().dissolve(dissolve_type, angle_limit, use_face_split, use_boundary_tear)
    )


@mcp.tool()
def mesh_tris_to_quads(
    ctx: Context,
    face_threshold: float = 40.0,
    shape_threshold: float = 40.0
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Converts triangles to quads where possible.

    Useful for:
    - Cleaning up triangulated imports (OBJ, FBX from game engines)
    - Post-boolean cleanup
    - Preparing mesh for subdivision surface
    - Better topology for animation deformation

    Workflow: BEFORE → mesh_select(action="all")

    Args:
        face_threshold: Max angle between face normals (degrees). Default 40.0.
        shape_threshold: Max shape difference for quad quality (degrees). Default 40.0.

    Examples:
        mesh_tris_to_quads() -> Convert with default thresholds
        mesh_tris_to_quads(face_threshold=60.0, shape_threshold=60.0) -> More aggressive conversion
    """
    return route_tool_call(
        tool_name="mesh_tris_to_quads",
        params={"face_threshold": face_threshold, "shape_threshold": shape_threshold},
        direct_executor=lambda: get_mesh_handler().tris_to_quads(face_threshold, shape_threshold)
    )


@mcp.tool()
def mesh_normals_make_consistent(
    ctx: Context,
    inside: bool = False
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Recalculates normals to face consistently.

    Fixes:
    - Inverted faces (black patches in render)
    - Inconsistent shading after boolean operations
    - Import artifacts from other 3D software

    Default: Normals face outward (standard for solid objects).
    Set inside=True for hollow objects like rooms/caves.

    Workflow: BEFORE → mesh_select(action="all")

    Args:
        inside: If True, flip normals to face inward. Default False (outward).

    Examples:
        mesh_normals_make_consistent() -> Fix normals facing outward
        mesh_normals_make_consistent(inside=True) -> Fix normals facing inward (for rooms)
    """
    return route_tool_call(
        tool_name="mesh_normals_make_consistent",
        params={"inside": inside},
        direct_executor=lambda: get_mesh_handler().normals_make_consistent(inside)
    )


@mcp.tool()
def mesh_decimate(
    ctx: Context,
    ratio: float = 0.5,
    use_symmetry: bool = False,
    symmetry_axis: Literal["X", "Y", "Z"] = "X"
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Reduces polycount while preserving shape.

    For whole-object decimation, prefer modeling_add_modifier(type="DECIMATE").
    This tool works on selected geometry only - useful for partial decimation.

    Use cases:
    - Creating LOD (Level of Detail) meshes for games
    - Optimizing dense sculpts for animation
    - Reducing polycount in specific areas

    Workflow: BEFORE → mesh_select(action="all") or select specific region

    Args:
        ratio: Target ratio (0.0-1.0). 0.5 = reduce by half. Default 0.5.
        use_symmetry: Maintain mesh symmetry during decimation. Default False.
        symmetry_axis: Axis for symmetry ("X", "Y", "Z"). Default "X".

    Examples:
        mesh_decimate(ratio=0.5) -> Reduce selected geometry by half
        mesh_decimate(ratio=0.25, use_symmetry=True) -> Aggressive reduction with symmetry
    """
    return route_tool_call(
        tool_name="mesh_decimate",
        params={"ratio": ratio, "use_symmetry": use_symmetry, "symmetry_axis": symmetry_axis},
        direct_executor=lambda: get_mesh_handler().decimate(ratio, use_symmetry, symmetry_axis)
    )


# ==============================================================================
# TASK-032: Knife & Cut Tools
# ==============================================================================

@mcp.tool()
def mesh_knife_project(
    ctx: Context,
    cut_through: bool = True
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Projects cut from selected geometry.

    Projects knife cut from view using selected edges/faces as cutter.
    Useful for: logo cutouts, panel lines, window frames, hard-surface details.

    IMPORTANT: Requires specific view angle for correct projection.
    Best used with orthographic views (Numpad 1, 3, 7).

    Requirements:
    - Object must be in Edit Mode
    - Select cutting geometry (edges/faces) in another object or same mesh
    - View angle determines projection direction

    Workflow: BEFORE → Position view orthographically, select cutter geometry

    Args:
        cut_through: If True, cuts through entire mesh. If False, only cuts visible faces.

    Examples:
        mesh_knife_project(cut_through=True) -> Cut through entire mesh
        mesh_knife_project(cut_through=False) -> Only cut visible faces from view
    """
    return route_tool_call(
        tool_name="mesh_knife_project",
        params={"cut_through": cut_through},
        direct_executor=lambda: get_mesh_handler().knife_project(cut_through)
    )


@mcp.tool()
def mesh_rip(
    ctx: Context,
    use_fill: bool = False
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Rips (tears) geometry at selection.

    Creates a hole/tear in the mesh at selected vertices or edges.
    Useful for: creating openings, tears, separating connected geometry.

    Note: Rips from the center of selection outward.

    Workflow: BEFORE → mesh_select_targeted(action="by_index", element_type="VERT")

    Args:
        use_fill: If True, fills the ripped hole with a face. Default False.

    Examples:
        mesh_rip() -> Rip at selected vertices
        mesh_rip(use_fill=True) -> Rip and fill the hole
    """
    return route_tool_call(
        tool_name="mesh_rip",
        params={"use_fill": use_fill},
        direct_executor=lambda: get_mesh_handler().rip(use_fill)
    )


@mcp.tool()
def mesh_split(ctx: Context) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Splits selection from mesh.

    Unlike 'separate' (which creates new objects), split keeps geometry
    in the same object but disconnects it from surrounding geometry.

    Useful for:
    - Creating movable parts that stay in the same object
    - Preparing geometry for animation
    - Isolating regions for material assignment
    - Pre-separation editing

    Workflow: BEFORE → mesh_select(action) or mesh_select_targeted | AFTER → mesh_transform_selected

    Examples:
        (select faces) mesh_split() -> Disconnect selected faces from rest of mesh
    """
    return route_tool_call(
        tool_name="mesh_split",
        params={},
        direct_executor=lambda: get_mesh_handler().split()
    )


@mcp.tool()
def mesh_edge_split(ctx: Context) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Splits mesh at selected edges.

    Creates a seam/split along selected edges. Geometry becomes disconnected
    but stays in place (vertices are duplicated at the split).

    Useful for:
    - UV seam preparation
    - Material boundaries
    - Rigging preparation (separating limbs)
    - Creating hard edges without modifiers

    Workflow: BEFORE → mesh_select_targeted(action="loop") | AFTER → mesh_transform_selected

    Examples:
        (select edge loop) mesh_edge_split() -> Split mesh along the edge loop
    """
    return route_tool_call(
        tool_name="mesh_edge_split",
        params={},
        direct_executor=lambda: get_mesh_handler().edge_split()
    )


# ==============================================================================
# TASK-038-5: Proportional Editing
# ==============================================================================


@mcp.tool()
def mesh_set_proportional_edit(
    ctx: Context,
    enabled: bool = True,
    falloff_type: Literal["SMOOTH", "SPHERE", "ROOT", "INVERSE_SQUARE", "SHARP", "LINEAR", "CONSTANT", "RANDOM"] = "SMOOTH",
    size: float = 1.0,
    use_connected: bool = False,
) -> str:
    """
    [EDIT MODE][SETTING] Configures proportional editing mode.

    Proportional editing affects nearby unselected geometry when transforming.
    Essential for organic modeling - creates smooth falloff in deformations.

    Falloff types:
    - SMOOTH: Smooth bell curve (default, best for organic shapes)
    - SPHERE: Spherical falloff (uniform distance-based)
    - ROOT: Square root falloff (faster initial falloff)
    - INVERSE_SQUARE: Inverse square falloff (sharp center, soft edges)
    - SHARP: Sharp falloff (aggressive center influence)
    - LINEAR: Linear falloff (even gradient)
    - CONSTANT: All affected vertices move equally
    - RANDOM: Randomized falloff (adds variation)

    Use connected=True to limit influence to connected geometry only
    (ignores other mesh islands/separate objects).

    Workflow: BEFORE → mesh_transform_selected | USE WITH → sculpt workflow prep

    Args:
        enabled: Enable or disable proportional editing (default True)
        falloff_type: Type of falloff curve (default SMOOTH)
        size: Radius of influence in Blender units (default 1.0)
        use_connected: Only affect connected geometry (default False)

    Examples:
        mesh_set_proportional_edit(enabled=True) -> Enable with defaults
        mesh_set_proportional_edit(falloff_type="SHARP", size=2.0) -> Sharp falloff, large area
        mesh_set_proportional_edit(use_connected=True) -> Only affect connected verts
        mesh_set_proportional_edit(enabled=False) -> Disable proportional editing
    """
    return route_tool_call(
        tool_name="mesh_set_proportional_edit",
        params={"enabled": enabled, "falloff_type": falloff_type, "size": size, "use_connected": use_connected},
        direct_executor=lambda: get_mesh_handler().set_proportional_edit(enabled, falloff_type, size, use_connected)
    )


# ==============================================================================
# TASK-036: Symmetry & Advanced Fill
# ==============================================================================

@mcp.tool()
def mesh_symmetrize(
    ctx: Context,
    direction: Literal["NEGATIVE_X", "POSITIVE_X", "NEGATIVE_Y", "POSITIVE_Y", "NEGATIVE_Z", "POSITIVE_Z"] = "NEGATIVE_X",
    threshold: float = 0.0001
) -> str:
    """
    [EDIT MODE][DESTRUCTIVE] Symmetrizes mesh.

    Mirrors geometry from one side to the other, making the mesh perfectly symmetric.
    Useful for:
    - Fixing asymmetric character models
    - Creating symmetric objects from half-models
    - Repair after asymmetric edits

    Direction examples:
    - NEGATIVE_X: Copy from +X to -X (right to left)
    - POSITIVE_X: Copy from -X to +X (left to right)

    Workflow: BEFORE → mesh_select(action="all") to symmetrize entire mesh

    Args:
        direction: Which side to copy FROM and TO. NEGATIVE_X = copy +X to -X.
        threshold: Distance threshold for merging mirrored vertices.

    Examples:
        mesh_symmetrize() -> Mirror right side to left (NEGATIVE_X)
        mesh_symmetrize(direction="POSITIVE_X") -> Mirror left side to right
        mesh_symmetrize(direction="NEGATIVE_Z") -> Mirror top to bottom
    """
    return route_tool_call(
        tool_name="mesh_symmetrize",
        params={"direction": direction, "threshold": threshold},
        direct_executor=lambda: get_mesh_handler().symmetrize(direction, threshold)
    )


@mcp.tool()
def mesh_grid_fill(
    ctx: Context,
    span: int = 1,
    offset: int = 0,
    use_interp_simple: bool = False
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Fills boundary with a grid of quads.

    Unlike mesh_fill_holes (which creates triangles), grid_fill creates
    a proper quad grid - essential for subdivision-ready topology.

    Requirements:
    - Selection must be a closed edge loop (boundary)
    - Works best with even number of edges

    Workflow: BEFORE → mesh_select(action="boundary") to select hole edge

    Args:
        span: Grid resolution (number of rows). Higher = denser grid.
        offset: Shifts the grid pattern alignment.
        use_interp_simple: Use simple interpolation (faster, less smooth).

    Examples:
        mesh_grid_fill() -> Fill with minimal quads
        mesh_grid_fill(span=4) -> Fill with 4-row grid
        mesh_grid_fill(span=2, offset=1) -> Shifted grid pattern
    """
    return route_tool_call(
        tool_name="mesh_grid_fill",
        params={"span": span, "offset": offset, "use_interp_simple": use_interp_simple},
        direct_executor=lambda: get_mesh_handler().grid_fill(span, offset, use_interp_simple)
    )


@mcp.tool()
def mesh_poke_faces(
    ctx: Context,
    offset: float = 0.0,
    use_relative_offset: bool = False,
    center_mode: Literal["MEDIAN", "MEDIAN_WEIGHTED", "BOUNDS"] = "MEDIAN_WEIGHTED"
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Pokes selected faces.

    Adds a vertex at the center of each selected face and connects to edges,
    creating a fan of triangles. Useful for:
    - Creating spikes/cones
    - Preparing for subdivision patterns
    - Artistic effects

    Workflow: BEFORE → mesh_select faces | Can combine with extrude for spikes

    Args:
        offset: Distance to push center vertex outward (negative = inward).
        use_relative_offset: Scale offset by face size.
        center_mode: How to calculate face center (MEDIAN, MEDIAN_WEIGHTED, BOUNDS).

    Examples:
        mesh_poke_faces() -> Poke faces with vertex at center
        mesh_poke_faces(offset=0.5) -> Poke and push center out (creates spikes)
        mesh_poke_faces(offset=-0.2) -> Poke and push center in (creates dimples)
    """
    return route_tool_call(
        tool_name="mesh_poke_faces",
        params={"offset": offset, "use_relative_offset": use_relative_offset, "center_mode": center_mode},
        direct_executor=lambda: get_mesh_handler().poke_faces(offset, use_relative_offset, center_mode)
    )


@mcp.tool()
def mesh_beautify_fill(
    ctx: Context,
    angle_limit: float = 180.0
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Beautifies face arrangement.

    Rotates triangle edges to create more uniform triangulation.
    Useful after:
    - Boolean operations
    - Triangulation
    - Import cleanup

    Workflow: BEFORE → mesh_select faces (select triangulated area)

    Args:
        angle_limit: Maximum angle for edge rotation (degrees). 180 = no limit.

    Examples:
        mesh_beautify_fill() -> Beautify all selected triangles
        mesh_beautify_fill(angle_limit=45.0) -> Only rotate edges below 45°
    """
    return route_tool_call(
        tool_name="mesh_beautify_fill",
        params={"angle_limit": angle_limit},
        direct_executor=lambda: get_mesh_handler().beautify_fill(angle_limit)
    )


@mcp.tool()
def mesh_mirror(
    ctx: Context,
    axis: Literal["X", "Y", "Z"] = "X",
    use_mirror_merge: bool = True,
    merge_threshold: float = 0.001
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Mirrors selected geometry.

    Unlike symmetrize (which replaces one side), mirror creates a copy.
    Useful for:
    - Duplicating symmetric parts
    - Creating mirrored elements

    For non-destructive mirroring, use modeling_add_modifier(type="MIRROR").

    Workflow: BEFORE → mesh_select geometry to mirror

    Args:
        axis: Axis to mirror across (X, Y, or Z).
        use_mirror_merge: Merge vertices at mirror plane.
        merge_threshold: Distance for merging mirrored vertices.

    Examples:
        mesh_mirror() -> Mirror selection across X axis
        mesh_mirror(axis="Y") -> Mirror across Y axis
        mesh_mirror(use_mirror_merge=False) -> Mirror without merging (keeps gap)
    """
    return route_tool_call(
        tool_name="mesh_mirror",
        params={"axis": axis, "use_mirror_merge": use_mirror_merge, "merge_threshold": merge_threshold},
        direct_executor=lambda: get_mesh_handler().mirror(axis, use_mirror_merge, merge_threshold)
    )
