from typing import Literal, Optional
from fastmcp import Context
from server.adapters.mcp.instance import mcp
from server.infrastructure.di import get_uv_handler

@mcp.tool()
def uv_list_maps(
    ctx: Context,
    object_name: str,
    include_island_counts: bool = False
) -> str:
    """
    [UV][SAFE][READ-ONLY] Lists UV maps on a mesh object.

    Workflow: READ-ONLY | USE → check UV setup before texturing

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


@mcp.tool()
def uv_unwrap(
    ctx: Context,
    object_name: Optional[str] = None,
    method: Literal["SMART_PROJECT", "CUBE", "CYLINDER", "SPHERE", "UNWRAP"] = "SMART_PROJECT",
    angle_limit: float = 66.0,
    island_margin: float = 0.02,
    scale_to_bounds: bool = True,
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Unwraps selected faces to UV space.

    Methods:
        - SMART_PROJECT: Automatic projection based on face angles (best for complex meshes)
        - CUBE: Cube projection (best for boxy objects)
        - CYLINDER: Cylindrical projection
        - SPHERE: Spherical projection
        - UNWRAP: Standard unwrap (requires seams for best results)

    Workflow: BEFORE → mesh_select (select faces) | AFTER → uv_pack_islands

    Args:
        object_name: Target object (default: active object)
        method: Unwrap projection method
        angle_limit: Angle threshold for SMART_PROJECT (degrees, 0-89)
        island_margin: Space between UV islands (0.0-1.0)
        scale_to_bounds: Scale UVs to fill 0-1 space
    """
    handler = get_uv_handler()
    try:
        result = handler.unwrap(
            object_name=object_name,
            method=method,
            angle_limit=angle_limit,
            island_margin=island_margin,
            scale_to_bounds=scale_to_bounds,
        )
        ctx.info(f"UV unwrap completed using {method}")
        return result
    except RuntimeError as e:
        msg = str(e)
        if "not found" in msg.lower():
            return f"{msg}. Use scene_list_objects to verify the object name."
        if "not a mesh" in msg.lower():
            return f"{msg}. UV operations only work on mesh objects."
        return msg


@mcp.tool()
def uv_pack_islands(
    ctx: Context,
    object_name: Optional[str] = None,
    margin: float = 0.02,
    rotate: bool = True,
    scale: bool = True,
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Packs UV islands for optimal texture space usage.

    Reorganizes UV islands to minimize wasted texture space while maintaining relative sizes.
    Best used after unwrapping to optimize the UV layout.

    Workflow: BEFORE → uv_unwrap

    Args:
        object_name: Target object (default: active object)
        margin: Space between packed islands (0.0-1.0)
        rotate: Allow rotation for better packing
        scale: Allow scaling islands to fill space
    """
    handler = get_uv_handler()
    try:
        result = handler.pack_islands(
            object_name=object_name,
            margin=margin,
            rotate=rotate,
            scale=scale,
        )
        ctx.info("UV islands packed")
        return result
    except RuntimeError as e:
        msg = str(e)
        if "not found" in msg.lower():
            return f"{msg}. Use scene_list_objects to verify the object name."
        if "not a mesh" in msg.lower():
            return f"{msg}. UV operations only work on mesh objects."
        return msg


@mcp.tool()
def uv_create_seam(
    ctx: Context,
    object_name: Optional[str] = None,
    action: Literal["mark", "clear"] = "mark",
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][NON-DESTRUCTIVE] Marks or clears UV seams on selected edges.

    Seams guide the UNWRAP method to split UV islands at specific edges.
    Mark seams along natural breaks (like shirt seams, box edges) for cleaner UV layouts.

    Workflow: BEFORE → mesh_select_targeted (select edges) | AFTER → uv_unwrap (with UNWRAP method)

    Args:
        object_name: Target object (default: active object)
        action: 'mark' to add seams, 'clear' to remove seams from selected edges
    """
    handler = get_uv_handler()
    try:
        result = handler.create_seam(
            object_name=object_name,
            action=action,
        )
        ctx.info(f"UV seam {action} completed")
        return result
    except RuntimeError as e:
        msg = str(e)
        if "not found" in msg.lower():
            return f"{msg}. Use scene_list_objects to verify the object name."
        if "not a mesh" in msg.lower():
            return f"{msg}. UV operations only work on mesh objects."
        return msg