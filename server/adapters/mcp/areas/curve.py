from typing import List, Literal, Optional
from fastmcp import Context
from server.adapters.mcp.instance import mcp
from server.infrastructure.di import get_curve_handler


# ==============================================================================
# TASK-021: Phase 2.6 - Curves & Procedural
# ==============================================================================

@mcp.tool()
def curve_create(
    ctx: Context,
    curve_type: Literal["BEZIER", "NURBS", "PATH", "CIRCLE"] = "BEZIER",
    location: Optional[List[float]] = None
) -> str:
    """
    [OBJECT MODE][SAFE] Creates a curve primitive object.
    Curves are non-destructive and can be converted to mesh via curve_to_mesh.

    Workflow: START → curve_to_mesh (if mesh needed) | USE FOR → paths, profiles, modeling guides

    Args:
        curve_type: Type of curve to create.
            - BEZIER: Bezier curve with control handles (default)
            - NURBS: NURBS curve for smooth surfaces
            - PATH: NURBS path for animation/follow paths
            - CIRCLE: Bezier circle (closed curve)
        location: Optional [x, y, z] position. Default is [0, 0, 0].

    Examples:
        curve_create(curve_type="BEZIER") -> Creates a Bezier curve at origin
        curve_create(curve_type="CIRCLE", location=[0, 0, 1]) -> Circle at Z=1
        curve_create(curve_type="PATH") -> Creates animation path
    """
    handler = get_curve_handler()
    try:
        return handler.create_curve(curve_type, location)
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def curve_to_mesh(
    ctx: Context,
    object_name: str
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Converts a curve object to mesh geometry.
    The curve is permanently converted - use modeling_add_modifier for non-destructive workflow.

    Workflow: BEFORE → curve_create | AFTER → mesh_* operations

    Args:
        object_name: Name of the curve object to convert.

    Examples:
        curve_to_mesh(object_name="BezierCurve") -> Converts curve to mesh
    """
    handler = get_curve_handler()
    try:
        return handler.curve_to_mesh(object_name)
    except RuntimeError as e:
        return str(e)
