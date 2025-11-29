from typing import List, Literal, Optional, Union
from fastmcp import Context
from server.adapters.mcp.instance import mcp
from server.adapters.mcp.utils import parse_coordinate
from server.infrastructure.di import get_mesh_handler


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
    handler = get_mesh_handler()
    try:
        return handler.delete_selected(type)
    except RuntimeError as e:
        return str(e)

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
    handler = get_mesh_handler()
    try:
        parsed_move = parse_coordinate(move)
        return handler.extrude_region(parsed_move)
    except (RuntimeError, ValueError) as e:
        return str(e)

@mcp.tool()
def mesh_fill_holes(ctx: Context) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Fills holes by creating faces from selected edges/vertices.
    Equivalent to pressing 'F' key in Blender.

    Workflow: BEFORE → mesh_select_boundary (CRITICAL!) | AFTER → mesh_merge_by_distance
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

    Workflow: BEFORE → mesh_select_loop, mesh_select_ring | AFTER → mesh_smooth

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

    Workflow: BEFORE → mesh_select_by_index(EDGE) | AFTER → mesh_select_loop

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

    Workflow: BEFORE → mesh_select_*(FACE) | AFTER → mesh_extrude_region

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

    Workflow: BEFORE → mesh_boolean, mesh_extrude | AFTER → mesh_smooth

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

    Workflow: BEFORE → mesh_select_* | AFTER → mesh_smooth

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

    Workflow: BEFORE → mesh_boolean, mesh_extrude, mesh_bevel | LAST STEP in edit workflow

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

    Workflow: BEFORE → mesh_select_by_location | USE FOR → creating flat surfaces

    Args:
        axis: Axis to flatten along ("X", "Y", or "Z")
    """
    handler = get_mesh_handler()
    try:
        return handler.flatten_vertices(axis)
    except RuntimeError as e:
        return str(e)
    
    
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
    handler = get_mesh_handler()
    try:
        result = handler.list_groups(object_name, group_type)
        import json
        
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
            
        ctx.info(f"Listed {count} {g_type} groups for '{obj_name}'")
        return "\n".join(lines)
        
    except RuntimeError as e:
        return str(e)
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
def mesh_get_vertex_data(
    ctx: Context,
    object_name: str,
    selected_only: bool = False
) -> str:
    """
    [EDIT MODE][READ-ONLY][SAFE] Returns vertex positions and selection states for programmatic analysis.

    Workflow: FIRST STEP for programmatic selection | AFTER → mesh_select_by_index, mesh_select_by_location

    This is a CRITICAL introspection tool that enables AI to make programmatic selection decisions
    based on geometry data. Does NOT modify the mesh - pure read operation.

    Args:
        object_name: Name of the object to inspect
        selected_only: If True, only return data for selected vertices (default: False)

    Returns:
        JSON string with vertex data:
        {
            "vertex_count": 8,
            "selected_count": 4,
            "vertices": [
                {"index": 0, "position": [1.0, 1.0, 1.0], "selected": true},
                {"index": 1, "position": [1.0, -1.0, 1.0], "selected": false}
            ]
        }

    Use cases:
        - Analyze vertex positions to determine selection strategy
        - Find vertices by coordinate ranges
        - Understand geometry before performing operations

    Example:
        mesh_get_vertex_data(object_name="Cube") -> Returns all vertex data
        mesh_get_vertex_data(object_name="Cube", selected_only=True) -> Returns only selected vertices
    """
    handler = get_mesh_handler()
    try:
        import json
        result = handler.get_vertex_data(object_name, selected_only)
        return json.dumps(result, indent=2)
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
    handler = get_mesh_handler()
    try:
        return handler.randomize(amount, uniform, normal, seed)
    except RuntimeError as e:
        return str(e)


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
    handler = get_mesh_handler()
    try:
        return handler.shrink_fatten(value)
    except RuntimeError as e:
        return str(e)


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
    handler = get_mesh_handler()
    try:
        return handler.create_vertex_group(object_name, name)
    except RuntimeError as e:
        return str(e)


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
    handler = get_mesh_handler()
    try:
        return handler.assign_to_group(object_name, group_name, weight)
    except RuntimeError as e:
        return str(e)


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
    handler = get_mesh_handler()
    try:
        return handler.remove_from_group(object_name, group_name)
    except RuntimeError as e:
        return str(e)
