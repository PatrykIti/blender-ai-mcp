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


# ==============================================================================
# TASK-038-2: Core Sculpt Brushes
# ==============================================================================


@mcp.tool()
def sculpt_brush_clay(
    ctx: Context,
    object_name: Optional[str] = None,
    radius: float = 0.1,
    strength: float = 0.5,
) -> str:
    """
    [SCULPT MODE][DESTRUCTIVE] Sets up Clay brush for adding material.

    Adds material like clay - builds up surface.
    Essential for: muscle mass, fat deposits, organ volume.

    Workflow: BEFORE -> scene_set_mode(mode='SCULPT')

    Args:
        object_name: Target object (default: active object)
        radius: Brush radius in Blender units (default 0.1)
        strength: Brush strength 0-1 (default 0.5)

    Examples:
        sculpt_brush_clay(radius=0.2, strength=0.6) -> Build up material
    """
    handler = get_sculpt_handler()
    try:
        return handler.brush_clay(
            object_name=object_name,
            radius=radius,
            strength=strength,
        )
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def sculpt_brush_inflate(
    ctx: Context,
    object_name: Optional[str] = None,
    radius: float = 0.1,
    strength: float = 0.5,
) -> str:
    """
    [SCULPT MODE][DESTRUCTIVE] Sets up Inflate brush for pushing geometry outward.

    Pushes geometry outward along normals - inflates like balloon.
    Essential for: swelling, tumors, blisters, organ volume.

    Workflow: BEFORE -> scene_set_mode(mode='SCULPT')

    Args:
        object_name: Target object (default: active object)
        radius: Brush radius in Blender units (default 0.1)
        strength: Brush strength 0-1 (default 0.5)

    Examples:
        sculpt_brush_inflate(radius=0.15, strength=0.4) -> Gentle inflation
    """
    handler = get_sculpt_handler()
    try:
        return handler.brush_inflate(
            object_name=object_name,
            radius=radius,
            strength=strength,
        )
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def sculpt_brush_blob(
    ctx: Context,
    object_name: Optional[str] = None,
    radius: float = 0.1,
    strength: float = 0.5,
) -> str:
    """
    [SCULPT MODE][DESTRUCTIVE] Sets up Blob brush for creating rounded organic bulges.

    Creates rounded, organic bulges.
    Essential for: nodules, bumps, organic growths.

    Workflow: BEFORE -> scene_set_mode(mode='SCULPT')

    Args:
        object_name: Target object (default: active object)
        radius: Brush radius in Blender units (default 0.1)
        strength: Brush strength 0-1 (default 0.5)

    Examples:
        sculpt_brush_blob(radius=0.1, strength=0.5) -> Create organic bumps
    """
    handler = get_sculpt_handler()
    try:
        return handler.brush_blob(
            object_name=object_name,
            radius=radius,
            strength=strength,
        )
    except RuntimeError as e:
        return str(e)


# ==============================================================================
# TASK-038-3: Detail Sculpt Brushes
# ==============================================================================


@mcp.tool()
def sculpt_brush_snake_hook(
    ctx: Context,
    object_name: Optional[str] = None,
    radius: float = 0.1,
    strength: float = 0.5,
) -> str:
    """
    [SCULPT MODE][DESTRUCTIVE] Sets up Snake Hook brush for pulling geometry like taffy.

    Pulls geometry like taffy - creates long tendrils.
    Essential for: blood vessels, nerves, tentacles, organic protrusions.

    Workflow: BEFORE -> scene_set_mode(mode='SCULPT')

    Args:
        object_name: Target object (default: active object)
        radius: Brush radius in Blender units (default 0.1)
        strength: Brush strength 0-1 (default 0.5)

    Examples:
        sculpt_brush_snake_hook(radius=0.08, strength=0.7) -> Pull tendrils
    """
    handler = get_sculpt_handler()
    try:
        return handler.brush_snake_hook(
            object_name=object_name,
            radius=radius,
            strength=strength,
        )
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def sculpt_brush_draw(
    ctx: Context,
    object_name: Optional[str] = None,
    radius: float = 0.1,
    strength: float = 0.5,
) -> str:
    """
    [SCULPT MODE][DESTRUCTIVE] Sets up Draw brush for basic sculpting.

    Basic sculpting - pushes/pulls surface.
    Essential for: general shaping, wrinkles, surface variation.

    Workflow: BEFORE -> scene_set_mode(mode='SCULPT')

    Args:
        object_name: Target object (default: active object)
        radius: Brush radius in Blender units (default 0.1)
        strength: Brush strength 0-1 (default 0.5)

    Examples:
        sculpt_brush_draw(radius=0.1, strength=0.5) -> General sculpting
    """
    handler = get_sculpt_handler()
    try:
        return handler.brush_draw(
            object_name=object_name,
            radius=radius,
            strength=strength,
        )
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def sculpt_brush_pinch(
    ctx: Context,
    object_name: Optional[str] = None,
    radius: float = 0.1,
    strength: float = 0.5,
) -> str:
    """
    [SCULPT MODE][DESTRUCTIVE] Sets up Pinch brush for pulling geometry toward center.

    Pulls geometry toward center - creates sharp creases.
    Essential for: wrinkles, folds, membrane attachments.

    Workflow: BEFORE -> scene_set_mode(mode='SCULPT')

    Args:
        object_name: Target object (default: active object)
        radius: Brush radius in Blender units (default 0.1)
        strength: Brush strength 0-1 (default 0.5)

    Examples:
        sculpt_brush_pinch(radius=0.05, strength=0.6) -> Create sharp folds
    """
    handler = get_sculpt_handler()
    try:
        return handler.brush_pinch(
            object_name=object_name,
            radius=radius,
            strength=strength,
        )
    except RuntimeError as e:
        return str(e)


# ==============================================================================
# TASK-038-4: Dynamic Topology (Dyntopo)
# ==============================================================================


@mcp.tool()
def sculpt_enable_dyntopo(
    ctx: Context,
    object_name: Optional[str] = None,
    detail_mode: Literal["RELATIVE", "CONSTANT", "BRUSH", "MANUAL"] = "RELATIVE",
    detail_size: float = 12.0,
    use_smooth_shading: bool = True,
) -> str:
    """
    [SCULPT MODE] Enables Dynamic Topology for automatic geometry addition.

    Dyntopo automatically adds/removes geometry as you sculpt.
    No need to worry about base mesh topology.

    Detail modes:
    - RELATIVE: Detail based on view distance (default)
    - CONSTANT: Fixed detail size in Blender units
    - BRUSH: Detail based on brush size
    - MANUAL: No automatic detail, use Flood Fill

    Essential for: sculpting from scratch, adding detail where needed.

    Warning: Destroys UV maps and vertex groups. Use for concept/base mesh.

    Workflow: BEFORE -> scene_set_mode(mode='SCULPT') | AFTER -> mesh_remesh_voxel

    Args:
        object_name: Target object (default: active object)
        detail_mode: RELATIVE, CONSTANT, BRUSH, MANUAL (default RELATIVE)
        detail_size: Detail level - pixels for RELATIVE, units for CONSTANT (default 12.0)
        use_smooth_shading: Use smooth shading (default True)

    Examples:
        sculpt_enable_dyntopo(detail_mode="RELATIVE", detail_size=8) -> Higher detail
        sculpt_enable_dyntopo(detail_mode="CONSTANT", detail_size=0.05) -> Fixed detail
    """
    handler = get_sculpt_handler()
    try:
        return handler.enable_dyntopo(
            object_name=object_name,
            detail_mode=detail_mode,
            detail_size=detail_size,
            use_smooth_shading=use_smooth_shading,
        )
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def sculpt_disable_dyntopo(
    ctx: Context,
    object_name: Optional[str] = None,
) -> str:
    """
    [SCULPT MODE] Disables Dynamic Topology.

    After disabling, consider mesh_remesh_voxel for clean topology.

    Workflow: AFTER -> sculpt_enable_dyntopo | AFTER -> mesh_remesh_voxel

    Args:
        object_name: Target object (default: active object)

    Examples:
        sculpt_disable_dyntopo() -> Turn off dyntopo for active object
    """
    handler = get_sculpt_handler()
    try:
        return handler.disable_dyntopo(
            object_name=object_name,
        )
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def sculpt_dyntopo_flood_fill(
    ctx: Context,
    object_name: Optional[str] = None,
) -> str:
    """
    [SCULPT MODE] Applies current detail level to entire mesh.

    Useful for: unifying detail level after sculpting.

    Workflow: BEFORE -> sculpt_enable_dyntopo

    Args:
        object_name: Target object (default: active object)

    Examples:
        sculpt_dyntopo_flood_fill() -> Apply detail to entire mesh
    """
    handler = get_sculpt_handler()
    try:
        return handler.dyntopo_flood_fill(
            object_name=object_name,
        )
    except RuntimeError as e:
        return str(e)
