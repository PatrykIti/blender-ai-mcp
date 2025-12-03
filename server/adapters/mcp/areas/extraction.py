"""MCP Tool definitions for Extraction Analysis Tools (TASK-044).

These tools support the Automatic Workflow Extraction System by providing
deep topology analysis, component detection, symmetry detection, and
multi-angle rendering for LLM Vision.
"""
import json
from typing import List, Optional
from fastmcp import Context
from server.adapters.mcp.instance import mcp
from server.adapters.mcp.router_helper import route_tool_call
from server.infrastructure.di import get_extraction_handler


@mcp.tool()
def extraction_deep_topology(
    ctx: Context,
    object_name: str
) -> str:
    """
    [OBJECT MODE][READ-ONLY][SAFE] Deep topology analysis for workflow extraction.

    Workflow: START → extraction pipeline | USE FOR → detecting mesh features

    Returns detailed analysis including:
    - Vertex/edge/face counts and types (tris/quads/ngons)
    - Edge loop detection and count
    - Face coplanarity groups
    - Estimated base primitive (CUBE, CYLINDER, SPHERE, etc.)
    - Feature indicators (beveled edges, inset faces, extrusions)

    Args:
        object_name: Name of the mesh object to analyze

    Returns:
        JSON with extended topology data
    """
    def execute():
        handler = get_extraction_handler()
        try:
            result = handler.deep_topology(object_name=object_name)
            ctx.info(f"Deep topology analysis completed for '{object_name}'")
            return json.dumps(result, indent=2)
        except RuntimeError as e:
            msg = str(e)
            if "not found" in msg.lower():
                return f"Object '{object_name}' not found. Use scene_list_objects to verify."
            if "not a mesh" in msg.lower():
                return f"Object '{object_name}' is not a mesh. Extraction tools only work on mesh objects."
            return msg

    return route_tool_call(
        tool_name="extraction_deep_topology",
        params={"object_name": object_name},
        direct_executor=execute
    )


@mcp.tool()
def extraction_component_separate(
    ctx: Context,
    object_name: str,
    min_vertex_count: int = 4
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Separates mesh into loose parts (components).

    Workflow: AFTER → import model | BEFORE → per-component analysis

    Creates separate objects for each disconnected mesh island.
    Filters out tiny components (less than min_vertex_count vertices).

    Args:
        object_name: Name of the mesh object to separate
        min_vertex_count: Minimum vertices to keep component (default 4)

    Returns:
        JSON with list of created component names and their stats
    """
    def execute():
        handler = get_extraction_handler()
        try:
            result = handler.component_separate(
                object_name=object_name,
                min_vertex_count=min_vertex_count
            )
            component_count = result.get("component_count", 0)
            ctx.info(f"Separated '{object_name}' into {component_count} components")
            return json.dumps(result, indent=2)
        except RuntimeError as e:
            msg = str(e)
            if "not found" in msg.lower():
                return f"Object '{object_name}' not found. Use scene_list_objects to verify."
            return msg

    return route_tool_call(
        tool_name="extraction_component_separate",
        params={"object_name": object_name, "min_vertex_count": min_vertex_count},
        direct_executor=execute
    )


@mcp.tool()
def extraction_detect_symmetry(
    ctx: Context,
    object_name: str,
    tolerance: float = 0.001
) -> str:
    """
    [OBJECT MODE][READ-ONLY][SAFE] Detects symmetry in mesh geometry.

    Workflow: AFTER → component_separate | USE FOR → mirror modifier detection

    Checks for symmetry along X, Y, Z axes by comparing vertex positions.
    Reports symmetry confidence for each axis.

    Args:
        object_name: Name of the mesh object to analyze
        tolerance: Distance tolerance for symmetry matching (default 0.001)

    Returns:
        JSON with symmetry info including axis confidence and symmetric pair counts
    """
    def execute():
        handler = get_extraction_handler()
        try:
            result = handler.detect_symmetry(
                object_name=object_name,
                tolerance=tolerance
            )
            x_sym = result.get("x_symmetric", False)
            y_sym = result.get("y_symmetric", False)
            z_sym = result.get("z_symmetric", False)

            symmetries = []
            if x_sym:
                symmetries.append("X")
            if y_sym:
                symmetries.append("Y")
            if z_sym:
                symmetries.append("Z")

            if symmetries:
                ctx.info(f"Detected symmetry on axes: {', '.join(symmetries)}")
            else:
                ctx.info("No symmetry detected")

            return json.dumps(result, indent=2)
        except RuntimeError as e:
            msg = str(e)
            if "not found" in msg.lower():
                return f"Object '{object_name}' not found. Use scene_list_objects to verify."
            return msg

    return route_tool_call(
        tool_name="extraction_detect_symmetry",
        params={"object_name": object_name, "tolerance": tolerance},
        direct_executor=execute
    )


@mcp.tool()
def extraction_edge_loop_analysis(
    ctx: Context,
    object_name: str
) -> str:
    """
    [OBJECT MODE][READ-ONLY][SAFE] Analyzes edge loops for feature detection.

    Workflow: AFTER → deep_topology | USE FOR → bevel/subdivision detection

    Detects:
    - Parallel edge loops (indicator of bevel or subdivision)
    - Edge loop spacing patterns
    - Support loops near corners
    - Chamfered edges

    Args:
        object_name: Name of the mesh object to analyze

    Returns:
        JSON with edge loop analysis including loop counts and feature detection
    """
    def execute():
        handler = get_extraction_handler()
        try:
            result = handler.edge_loop_analysis(object_name=object_name)
            loop_count = result.get("total_edge_loops", 0)
            ctx.info(f"Analyzed {loop_count} edge loops in '{object_name}'")
            return json.dumps(result, indent=2)
        except RuntimeError as e:
            msg = str(e)
            if "not found" in msg.lower():
                return f"Object '{object_name}' not found. Use scene_list_objects to verify."
            return msg

    return route_tool_call(
        tool_name="extraction_edge_loop_analysis",
        params={"object_name": object_name},
        direct_executor=execute
    )


@mcp.tool()
def extraction_face_group_analysis(
    ctx: Context,
    object_name: str,
    angle_threshold: float = 5.0
) -> str:
    """
    [OBJECT MODE][READ-ONLY][SAFE] Analyzes face groups for feature detection.

    Workflow: AFTER → deep_topology | USE FOR → inset/extrude detection

    Groups faces by:
    - Normal direction (coplanar faces)
    - Height/position (Z-level groups)
    - Connectivity (adjacent face regions)

    Detects:
    - Inset faces (face surrounded by thin quad border)
    - Extruded regions (face groups at different heights)
    - Planar regions (large coplanar face groups)

    Args:
        object_name: Name of the mesh object to analyze
        angle_threshold: Max angle difference for coplanar grouping (degrees)

    Returns:
        JSON with face group analysis including detected features
    """
    def execute():
        handler = get_extraction_handler()
        try:
            result = handler.face_group_analysis(
                object_name=object_name,
                angle_threshold=angle_threshold
            )
            group_count = len(result.get("face_groups", []))
            ctx.info(f"Analyzed {group_count} face groups in '{object_name}'")
            return json.dumps(result, indent=2)
        except RuntimeError as e:
            msg = str(e)
            if "not found" in msg.lower():
                return f"Object '{object_name}' not found. Use scene_list_objects to verify."
            return msg

    return route_tool_call(
        tool_name="extraction_face_group_analysis",
        params={"object_name": object_name, "angle_threshold": angle_threshold},
        direct_executor=execute
    )


@mcp.tool()
def extraction_render_angles(
    ctx: Context,
    object_name: str,
    angles: Optional[List[str]] = None,
    resolution: int = 512,
    output_dir: str = "/tmp/extraction_renders"
) -> str:
    """
    [OBJECT MODE][SAFE] Renders object from multiple angles for LLM Vision analysis.

    Workflow: AFTER → component analysis | USE FOR → LLM Vision semantic extraction

    Renders the object from predefined angles:
    - front: Y- direction
    - back: Y+ direction
    - left: X- direction
    - right: X+ direction
    - top: Z+ direction (looking down)
    - iso: Isometric view (45° from front-right-top)

    Args:
        object_name: Object to render (others will be hidden)
        angles: List of angles to render (default: all 6)
        resolution: Image resolution in pixels (default 512)
        output_dir: Directory to save renders

    Returns:
        JSON with render paths for each angle
    """
    def execute():
        handler = get_extraction_handler()
        try:
            result = handler.render_angles(
                object_name=object_name,
                angles=angles,
                resolution=resolution,
                output_dir=output_dir
            )
            render_count = len(result.get("renders", []))
            ctx.info(f"Rendered {render_count} views of '{object_name}'")
            return json.dumps(result, indent=2)
        except RuntimeError as e:
            msg = str(e)
            if "not found" in msg.lower():
                return f"Object '{object_name}' not found. Use scene_list_objects to verify."
            return msg

    return route_tool_call(
        tool_name="extraction_render_angles",
        params={
            "object_name": object_name,
            "angles": angles,
            "resolution": resolution,
            "output_dir": output_dir
        },
        direct_executor=execute
    )
