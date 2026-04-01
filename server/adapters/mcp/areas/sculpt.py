from typing import Any, Dict, List, Literal, Optional

from fastmcp import Context

from server.adapters.mcp.areas._registration import register_existing_tools
from server.adapters.mcp.router_helper import route_tool_call
from server.adapters.mcp.utils import parse_coordinate
from server.adapters.mcp.visibility.tags import get_capability_tags
from server.infrastructure.di import get_sculpt_handler

SCULPT_PUBLIC_TOOL_NAMES = (
    "sculpt_auto",
    "sculpt_deform_region",
    "sculpt_crease_region",
    "sculpt_smooth_region",
    "sculpt_inflate_region",
    "sculpt_pinch_region",
    "sculpt_enable_dyntopo",
    "sculpt_disable_dyntopo",
    "sculpt_dyntopo_flood_fill",
)


def register_sculpt_tools(target: Any) -> Dict[str, Any]:
    """Register public sculpt tools on a FastMCP server or LocalProvider."""

    return register_existing_tools(globals(), target, SCULPT_PUBLIC_TOOL_NAMES, tags=get_capability_tags("sculpt"))


# ==============================================================================
# TASK-027: Sculpting Tools
# ==============================================================================


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
    return route_tool_call(
        tool_name="sculpt_auto",
        params={
            "operation": operation,
            "object_name": object_name,
            "strength": strength,
            "iterations": iterations,
            "use_symmetry": use_symmetry,
            "symmetry_axis": symmetry_axis,
        },
        direct_executor=lambda: get_sculpt_handler().auto_sculpt(
            object_name=object_name,
            operation=operation,
            strength=strength,
            iterations=iterations,
            use_symmetry=use_symmetry,
            symmetry_axis=symmetry_axis,
        ),
    )


def sculpt_deform_region(
    ctx: Context,
    object_name: Optional[str] = None,
    center: List[float] | str | None = None,
    radius: float = 0.5,
    delta: List[float] | str | None = None,
    strength: float = 1.0,
    falloff: Literal["SMOOTH", "LINEAR", "SHARP", "CONSTANT"] = "SMOOTH",
    use_symmetry: bool = False,
    symmetry_axis: Literal["X", "Y", "Z"] = "X",
) -> str:
    """
    [OBJECT/SCULPT MODE][DETERMINISTIC][DESTRUCTIVE] Deforms a local mesh region by a weighted delta vector.

    This is the programmatic replacement for brush-style grab deformation.
    It operates directly on mesh data, not on viewport-driven brush strokes,
    so it is stable and suitable for LLM automation.

    Workflow: BEFORE -> inspect_scene / mesh_inspect | AFTER -> scene_snapshot_state / scene_compare_snapshot

    Args:
        object_name: Target object (default: active object)
        center: World-space center of influence [x, y, z]
        radius: Radius of influence in Blender units
        delta: World-space displacement vector [x, y, z]
        strength: Blend factor 0-1 applied to the weighted deformation
        falloff: Weight curve inside the radius (`SMOOTH`, `LINEAR`, `SHARP`, `CONSTANT`)
        use_symmetry: If True, mirrors the deformation across the chosen axis
        symmetry_axis: Symmetry axis (`X`, `Y`, `Z`)

    Examples:
        sculpt_deform_region(object_name="Head", center=[0,0,1], radius=0.35, delta=[0,0,0.2])
        sculpt_deform_region(object_name="Arm", center=[0.5,0,0], radius=0.2, delta=[0.1,0,0], use_symmetry=True, symmetry_axis="X")
    """

    def execute():
        handler = get_sculpt_handler()
        try:
            parsed_center = parse_coordinate(center)
            parsed_delta = parse_coordinate(delta)
            return handler.deform_region(
                object_name=object_name,
                center=parsed_center,
                radius=radius,
                delta=parsed_delta,
                strength=strength,
                falloff=falloff,
                use_symmetry=use_symmetry,
                symmetry_axis=symmetry_axis,
            )
        except (RuntimeError, ValueError) as e:
            return str(e)

    return route_tool_call(
        tool_name="sculpt_deform_region",
        params={
            "object_name": object_name,
            "center": center,
            "radius": radius,
            "delta": delta,
            "strength": strength,
            "falloff": falloff,
            "use_symmetry": use_symmetry,
            "symmetry_axis": symmetry_axis,
        },
        direct_executor=execute,
    )


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
    return route_tool_call(
        tool_name="sculpt_brush_smooth",
        params={"object_name": object_name, "location": location, "radius": radius, "strength": strength},
        direct_executor=lambda: get_sculpt_handler().brush_smooth(
            object_name=object_name, location=location, radius=radius, strength=strength
        ),
    )


def sculpt_smooth_region(
    ctx: Context,
    object_name: Optional[str] = None,
    center: List[float] | str | None = None,
    radius: float = 0.5,
    strength: float = 0.5,
    iterations: int = 1,
    falloff: Literal["SMOOTH", "LINEAR", "SHARP", "CONSTANT"] = "SMOOTH",
    use_symmetry: bool = False,
    symmetry_axis: Literal["X", "Y", "Z"] = "X",
) -> str:
    """
    [OBJECT/SCULPT MODE][DETERMINISTIC][DESTRUCTIVE] Smooths a local mesh region using edge-adjacency averaging.

    This is the programmatic replacement for brush-style smooth setup. It operates
    directly on mesh data and is suitable for repeatable LLM-driven workflows.
    """

    def execute():
        handler = get_sculpt_handler()
        try:
            parsed_center = parse_coordinate(center)
            return handler.smooth_region(
                object_name=object_name,
                center=parsed_center,
                radius=radius,
                strength=strength,
                iterations=iterations,
                falloff=falloff,
                use_symmetry=use_symmetry,
                symmetry_axis=symmetry_axis,
            )
        except (RuntimeError, ValueError) as e:
            return str(e)

    return route_tool_call(
        tool_name="sculpt_smooth_region",
        params={
            "object_name": object_name,
            "center": center,
            "radius": radius,
            "strength": strength,
            "iterations": iterations,
            "falloff": falloff,
            "use_symmetry": use_symmetry,
            "symmetry_axis": symmetry_axis,
        },
        direct_executor=execute,
    )


def sculpt_brush_grab(
    ctx: Context,
    object_name: Optional[str] = None,
    from_location: Optional[List[float]] = None,
    to_location: Optional[List[float]] = None,
    radius: float = 0.1,
    strength: float = 0.5,
) -> str:
    """
    [SCULPT MODE][SETUP-ONLY][NON-DESTRUCTIVE] Configures the Grab brush for manual interaction.

    This tool does not execute a sculpt stroke. It only switches to the Grab brush,
    applies radius/strength settings, and records the intended from/to locations in
    the returned message for operator context.

    For reliable programmatic geometry changes, prefer mesh tools like
    mesh_transform_selected with careful vertex selection.

    Workflow: BEFORE -> scene_set_mode(mode='SCULPT')

    Args:
        object_name: Target object (default: active object)
        from_location: Intended start position [x, y, z] for a manual grab stroke
        to_location: Intended end position [x, y, z] for a manual grab stroke
        radius: Brush radius (default 0.1)
        strength: Brush strength 0-1 (default 0.5)

    Examples:
        sculpt_brush_grab(from_location=[0,0,0], to_location=[0,0,0.5], radius=0.2)
        -> configures the brush only; does not move geometry by itself
    """
    return route_tool_call(
        tool_name="sculpt_brush_grab",
        params={
            "object_name": object_name,
            "from_location": from_location,
            "to_location": to_location,
            "radius": radius,
            "strength": strength,
        },
        direct_executor=lambda: get_sculpt_handler().brush_grab(
            object_name=object_name,
            from_location=from_location,
            to_location=to_location,
            radius=radius,
            strength=strength,
        ),
    )


def sculpt_inflate_region(
    ctx: Context,
    object_name: Optional[str] = None,
    center: List[float] | str | None = None,
    radius: float = 0.5,
    amount: float = 0.2,
    falloff: Literal["SMOOTH", "LINEAR", "SHARP", "CONSTANT"] = "SMOOTH",
    use_symmetry: bool = False,
    symmetry_axis: Literal["X", "Y", "Z"] = "X",
) -> str:
    """
    [OBJECT/SCULPT MODE][DETERMINISTIC][DESTRUCTIVE] Inflates or deflates a local mesh region.

    This is the programmatic replacement for brush-style local inflate behavior.
    """

    def execute():
        handler = get_sculpt_handler()
        try:
            parsed_center = parse_coordinate(center)
            return handler.inflate_region(
                object_name=object_name,
                center=parsed_center,
                radius=radius,
                amount=amount,
                falloff=falloff,
                use_symmetry=use_symmetry,
                symmetry_axis=symmetry_axis,
            )
        except (RuntimeError, ValueError) as e:
            return str(e)

    return route_tool_call(
        tool_name="sculpt_inflate_region",
        params={
            "object_name": object_name,
            "center": center,
            "radius": radius,
            "amount": amount,
            "falloff": falloff,
            "use_symmetry": use_symmetry,
            "symmetry_axis": symmetry_axis,
        },
        direct_executor=execute,
    )


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
    return route_tool_call(
        tool_name="sculpt_brush_crease",
        params={
            "object_name": object_name,
            "location": location,
            "radius": radius,
            "strength": strength,
            "pinch": pinch,
        },
        direct_executor=lambda: get_sculpt_handler().brush_crease(
            object_name=object_name, location=location, radius=radius, strength=strength, pinch=pinch
        ),
    )


def sculpt_pinch_region(
    ctx: Context,
    object_name: Optional[str] = None,
    center: List[float] | str | None = None,
    radius: float = 0.5,
    amount: float = 0.2,
    falloff: Literal["SMOOTH", "LINEAR", "SHARP", "CONSTANT"] = "SMOOTH",
    use_symmetry: bool = False,
    symmetry_axis: Literal["X", "Y", "Z"] = "X",
) -> str:
    """
    [OBJECT/SCULPT MODE][DETERMINISTIC][DESTRUCTIVE] Pinches a local mesh region toward the influence center.

    This is the programmatic replacement for brush-style pinch setup.
    """

    def execute():
        handler = get_sculpt_handler()
        try:
            parsed_center = parse_coordinate(center)
            return handler.pinch_region(
                object_name=object_name,
                center=parsed_center,
                radius=radius,
                amount=amount,
                falloff=falloff,
                use_symmetry=use_symmetry,
                symmetry_axis=symmetry_axis,
            )
        except (RuntimeError, ValueError) as e:
            return str(e)

    return route_tool_call(
        tool_name="sculpt_pinch_region",
        params={
            "object_name": object_name,
            "center": center,
            "radius": radius,
            "amount": amount,
            "falloff": falloff,
            "use_symmetry": use_symmetry,
            "symmetry_axis": symmetry_axis,
        },
        direct_executor=execute,
    )


def sculpt_crease_region(
    ctx: Context,
    object_name: Optional[str] = None,
    center: List[float] | str | None = None,
    radius: float = 0.5,
    depth: float = 0.1,
    pinch: float = 0.5,
    falloff: Literal["SMOOTH", "LINEAR", "SHARP", "CONSTANT"] = "SMOOTH",
    use_symmetry: bool = False,
    symmetry_axis: Literal["X", "Y", "Z"] = "X",
) -> str:
    """
    [OBJECT/SCULPT MODE][DETERMINISTIC][DESTRUCTIVE] Creates a local crease/groove region.

    This is the programmatic replacement for brush-style crease behavior.
    """

    def execute():
        handler = get_sculpt_handler()
        try:
            parsed_center = parse_coordinate(center)
            return handler.crease_region(
                object_name=object_name,
                center=parsed_center,
                radius=radius,
                depth=depth,
                pinch=pinch,
                falloff=falloff,
                use_symmetry=use_symmetry,
                symmetry_axis=symmetry_axis,
            )
        except (RuntimeError, ValueError) as e:
            return str(e)

    return route_tool_call(
        tool_name="sculpt_crease_region",
        params={
            "object_name": object_name,
            "center": center,
            "radius": radius,
            "depth": depth,
            "pinch": pinch,
            "falloff": falloff,
            "use_symmetry": use_symmetry,
            "symmetry_axis": symmetry_axis,
        },
        direct_executor=execute,
    )


# ==============================================================================
# TASK-038-2: Core Sculpt Brushes
# ==============================================================================


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
    return route_tool_call(
        tool_name="sculpt_brush_clay",
        params={"object_name": object_name, "radius": radius, "strength": strength},
        direct_executor=lambda: get_sculpt_handler().brush_clay(
            object_name=object_name, radius=radius, strength=strength
        ),
    )


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
    return route_tool_call(
        tool_name="sculpt_brush_inflate",
        params={"object_name": object_name, "radius": radius, "strength": strength},
        direct_executor=lambda: get_sculpt_handler().brush_inflate(
            object_name=object_name, radius=radius, strength=strength
        ),
    )


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
    return route_tool_call(
        tool_name="sculpt_brush_blob",
        params={"object_name": object_name, "radius": radius, "strength": strength},
        direct_executor=lambda: get_sculpt_handler().brush_blob(
            object_name=object_name, radius=radius, strength=strength
        ),
    )


# ==============================================================================
# TASK-038-3: Detail Sculpt Brushes
# ==============================================================================


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
    return route_tool_call(
        tool_name="sculpt_brush_snake_hook",
        params={"object_name": object_name, "radius": radius, "strength": strength},
        direct_executor=lambda: get_sculpt_handler().brush_snake_hook(
            object_name=object_name, radius=radius, strength=strength
        ),
    )


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
    return route_tool_call(
        tool_name="sculpt_brush_draw",
        params={"object_name": object_name, "radius": radius, "strength": strength},
        direct_executor=lambda: get_sculpt_handler().brush_draw(
            object_name=object_name, radius=radius, strength=strength
        ),
    )


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
    return route_tool_call(
        tool_name="sculpt_brush_pinch",
        params={"object_name": object_name, "radius": radius, "strength": strength},
        direct_executor=lambda: get_sculpt_handler().brush_pinch(
            object_name=object_name, radius=radius, strength=strength
        ),
    )


# ==============================================================================
# TASK-038-4: Dynamic Topology (Dyntopo)
# ==============================================================================


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
    return route_tool_call(
        tool_name="sculpt_enable_dyntopo",
        params={
            "object_name": object_name,
            "detail_mode": detail_mode,
            "detail_size": detail_size,
            "use_smooth_shading": use_smooth_shading,
        },
        direct_executor=lambda: get_sculpt_handler().enable_dyntopo(
            object_name=object_name,
            detail_mode=detail_mode,
            detail_size=detail_size,
            use_smooth_shading=use_smooth_shading,
        ),
    )


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
    return route_tool_call(
        tool_name="sculpt_disable_dyntopo",
        params={"object_name": object_name},
        direct_executor=lambda: get_sculpt_handler().disable_dyntopo(object_name=object_name),
    )


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
    return route_tool_call(
        tool_name="sculpt_dyntopo_flood_fill",
        params={"object_name": object_name},
        direct_executor=lambda: get_sculpt_handler().dyntopo_flood_fill(object_name=object_name),
    )
