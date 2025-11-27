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