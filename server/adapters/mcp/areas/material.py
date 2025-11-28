from fastmcp import Context
from server.adapters.mcp.instance import mcp
from server.infrastructure.di import get_material_handler

@mcp.tool()
def material_list(ctx: Context, include_unassigned: bool = True) -> str:
    """
    [MATERIAL][SAFE][READ-ONLY] Lists materials with shader parameters and assignment counts.

    Workflow: READ-ONLY | USE → find materials to assign

    Args:
        include_unassigned: If True, includes materials not assigned to any object
    """
    handler = get_material_handler()
    try:
        materials = handler.list_materials(include_unassigned=include_unassigned)

        if not materials:
            return "No materials found in the scene."

        lines = [f"Materials ({len(materials)}):"]
        for mat in materials:
            name = mat["name"]
            uses_nodes = mat.get("use_nodes", False)
            assigned = mat.get("assigned_object_count", 0)

            details = []
            if not uses_nodes:
                details.append("legacy")
            if assigned == 0:
                details.append("unassigned")

            detail_str = f" [{', '.join(details)}]" if details else ""

            lines.append(f"  • {name} (objects: {assigned}){detail_str}")

            # Add shader params if available
            if "base_color" in mat:
                rgb = mat["base_color"]
                lines.append(f"      Color: RGB{rgb}, Roughness: {mat.get('roughness', 'N/A')}, Metallic: {mat.get('metallic', 'N/A')}")

        ctx.info(f"Listed {len(materials)} materials")
        return "\n".join(lines)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def material_list_by_object(ctx: Context, object_name: str, include_indices: bool = False) -> str:
    """
    [MATERIAL][SAFE][READ-ONLY] Lists material slots for a given object.

    Workflow: READ-ONLY | USE WITH → scene_inspect_material_slots

    Args:
        object_name: Name of the object to query
        include_indices: If True, attempts to include face-level assignment info
    """
    handler = get_material_handler()
    try:
        result = handler.list_by_object(object_name=object_name, include_indices=include_indices)

        slots = result.get("slots", [])
        slot_count = result.get("slot_count", 0)

        if slot_count == 0:
            return f"Object '{object_name}' has no material slots."

        lines = [
            f"Object: {object_name}",
            f"Material Slots ({slot_count}):"
        ]

        for slot in slots:
            mat_name = slot.get("material_name") or "<empty>"
            idx = slot.get("slot_index")
            uses_nodes = " [nodes]" if slot.get("uses_nodes") else ""

            lines.append(f"  [{idx}] {slot.get('slot_name')}: {mat_name}{uses_nodes}")

            if "note" in slot:
                lines.append(f"      Note: {slot['note']}")

        ctx.info(f"Listed {slot_count} material slots for '{object_name}'")
        return "\n".join(lines)
    except RuntimeError as e:
        msg = str(e)
        if "not found" in msg.lower():
            return f"{msg}. Use scene_list_objects to verify the name."
        return msg