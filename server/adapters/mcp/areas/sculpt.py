from typing import List, Literal, Optional

from fastmcp import Context

from server.adapters.mcp.instance import mcp
from server.infrastructure.di import get_sculpt_handler


# ==============================================================================
# TASK-027: Sculpting Tools
# ==============================================================================


@mcp.tool()
def sculpt_auto(
    ctx: Context,
    operation: Literal["smooth", "inflate", "flatten", "sharpen"] = "smooth",
    object_name: Optional[str] = None,
    strength: float = 0.5,
    iterations: int = 1,
    use_symmetry: bool = True,
    symmetry_axis: Literal["X", "Y", "Z"] = "X",
) -> str:
    """
    [SCULPT MODE][DESTRUCTIVE] High-level sculpt operation applied to entire mesh.

    Uses Blender's mesh filters for consistent, whole-mesh sculpting operations.
    More reliable for AI workflows than brush strokes.

    Operations:
        - smooth: Smooths the entire surface (removes noise, softens details)
        - inflate: Expands mesh outward along normals (adds volume)
        - flatten: Flattens surface irregularities (creates planar areas)
        - sharpen: Enhances surface detail and edges

    Note: Object must be in Sculpt Mode. Use scene_set_mode(mode='SCULPT') first.

    Workflow: BEFORE -> scene_set_mode(mode='SCULPT') | AFTER -> mesh_remesh_voxel

    Args:
        operation: Sculpt operation type
        object_name: Target object (default: active object)
        strength: Operation strength 0-1 (default 0.5)
        iterations: Number of passes (default 1)
        use_symmetry: Enable symmetry (default True)
        symmetry_axis: Symmetry axis (default X)

    Examples:
        sculpt_auto(operation="smooth", iterations=3) -> Smooth whole mesh 3 times
        sculpt_auto(operation="inflate", strength=0.3) -> Gentle inflation
        sculpt_auto(operation="flatten", use_symmetry=False) -> Flatten without symmetry
    """
    handler = get_sculpt_handler()
    try:
        return handler.auto_sculpt(
            object_name=object_name,
            operation=operation,
            strength=strength,
            iterations=iterations,
            use_symmetry=use_symmetry,
            symmetry_axis=symmetry_axis,
        )
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def sculpt_brush_smooth(
    ctx: Context,
    object_name: Optional[str] = None,
    location: Optional[List[float]] = None,
    radius: float = 0.1,
    strength: float = 0.5,
) -> str:
    """
    [SCULPT MODE][DESTRUCTIVE] Applies smooth brush at specified location.

    Note: Programmatic brush strokes in Blender are complex. This tool sets up
    the brush and context. For whole-mesh smoothing, prefer sculpt_auto(operation='smooth').

    Workflow: BEFORE -> scene_set_mode(mode='SCULPT'), mesh_get_vertex_data

    Args:
        object_name: Target object (default: active object)
        location: World position [x, y, z] for brush center (optional)
        radius: Brush radius in Blender units (default 0.1)
        strength: Brush strength 0-1 (default 0.5)

    Examples:
        sculpt_brush_smooth(radius=0.2, strength=0.8) -> High-strength smooth brush
        sculpt_brush_smooth(location=[0, 0, 1], radius=0.15) -> Smooth at specific location
    """
    handler = get_sculpt_handler()
    try:
        return handler.brush_smooth(
            object_name=object_name,
            location=location,
            radius=radius,
            strength=strength,
        )
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def sculpt_brush_grab(
    ctx: Context,
    object_name: Optional[str] = None,
    from_location: Optional[List[float]] = None,
    to_location: Optional[List[float]] = None,
    radius: float = 0.1,
    strength: float = 0.5,
) -> str:
    """
    [SCULPT MODE][DESTRUCTIVE] Grabs and moves geometry from one location to another.

    Note: Programmatic brush strokes are complex. For reliable results, consider using
    mesh tools like mesh_transform_selected with careful vertex selection.

    Workflow: BEFORE -> scene_set_mode(mode='SCULPT')

    Args:
        object_name: Target object (default: active object)
        from_location: Start position [x, y, z] for grab
        to_location: End position [x, y, z] where to move
        radius: Brush radius (default 0.1)
        strength: Brush strength 0-1 (default 0.5)

    Examples:
        sculpt_brush_grab(from_location=[0,0,0], to_location=[0,0,0.5], radius=0.2)
    """
    handler = get_sculpt_handler()
    try:
        return handler.brush_grab(
            object_name=object_name,
            from_location=from_location,
            to_location=to_location,
            radius=radius,
            strength=strength,
        )
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def sculpt_brush_crease(
    ctx: Context,
    object_name: Optional[str] = None,
    location: Optional[List[float]] = None,
    radius: float = 0.1,
    strength: float = 0.5,
    pinch: float = 0.5,
) -> str:
    """
    [SCULPT MODE][DESTRUCTIVE] Creates sharp crease at specified location.

    Useful for creating defined lines, wrinkles, or sharp edge details.

    Note: Programmatic brush strokes are complex. For sharp edges, consider using
    mesh tools like mesh_bevel with careful edge selection.

    Workflow: BEFORE -> scene_set_mode(mode='SCULPT')

    Args:
        object_name: Target object (default: active object)
        location: World position [x, y, z] for crease (optional)
        radius: Brush radius (default 0.1)
        strength: Brush strength 0-1 (default 0.5)
        pinch: Pinch amount for sharper creases 0-1 (default 0.5)

    Examples:
        sculpt_brush_crease(location=[0,0,1], radius=0.05, strength=0.8) -> Sharp crease
        sculpt_brush_crease(pinch=0.9) -> Very sharp pinched crease
    """
    handler = get_sculpt_handler()
    try:
        return handler.brush_crease(
            object_name=object_name,
            location=location,
            radius=radius,
            strength=strength,
            pinch=pinch,
        )
    except RuntimeError as e:
        return str(e)
