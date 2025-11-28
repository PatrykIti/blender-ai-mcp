from typing import List, Optional, Union
from fastmcp import Context
from server.adapters.mcp.instance import mcp
from server.adapters.mcp.utils import parse_coordinate
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
def mesh_extrude_region(ctx: Context, move: Union[str, List[float], None] = None) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Extrudes selected geometry.
    WARNING: If 'move' is None, new geometry is created in-place (overlapping).
    Always provide 'move' vector or follow up with transform.

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
    solver: str = 'EXACT'
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
    
    
@mcp.tool()
def mesh_list_groups(
    ctx: Context,
    object_name: str,
    group_type: str = 'VERTEX'
) -> str:
    """
    [MESH][SAFE][READ-ONLY] Lists vertex/face groups defined on mesh.
    
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
@mcp.tool()
def mesh_select_loop(
    ctx: Context,
    edge_index: int
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Selects an edge loop based on the target edge index.
    
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

@mcp.tool()
def mesh_select_ring(
    ctx: Context,
    edge_index: int
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Selects an edge ring based on the target edge index.
    
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
