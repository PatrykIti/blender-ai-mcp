from typing import List, Optional, Union
from fastmcp import Context
from server.adapters.mcp.instance import mcp
from server.adapters.mcp.context_utils import ctx_info
from server.adapters.mcp.router_helper import route_tool_call
from server.adapters.mcp.utils import parse_coordinate
from server.infrastructure.di import get_material_handler


@mcp.tool()
def material_list(ctx: Context, include_unassigned: bool = True) -> str:
    """
    [MATERIAL][SAFE][READ-ONLY] Lists materials with shader parameters and assignment counts.

    Workflow: READ-ONLY | USE → find materials to assign

    Args:
        include_unassigned: If True, includes materials not assigned to any object
    """
    def execute():
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

                if "base_color" in mat:
                    rgb = mat["base_color"]
                    lines.append(f"      Color: RGB{rgb}, Roughness: {mat.get('roughness', 'N/A')}, Metallic: {mat.get('metallic', 'N/A')}")

            ctx_info(ctx, f"Listed {len(materials)} materials")
            return "\n".join(lines)
        except (RuntimeError, ValueError) as e:
            return str(e)

    return route_tool_call(
        tool_name="material_list",
        params={"include_unassigned": include_unassigned},
        direct_executor=execute
    )


@mcp.tool()
def material_list_by_object(ctx: Context, object_name: str, include_indices: bool = False) -> str:
    """
    [MATERIAL][SAFE][READ-ONLY] Lists material slots for a given object.

    Workflow: READ-ONLY | USE WITH → scene_inspect_material_slots

    Args:
        object_name: Name of the object to query
        include_indices: If True, attempts to include face-level assignment info
    """
    def execute():
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

            ctx_info(ctx, f"Listed {slot_count} material slots for '{object_name}'")
            return "\n".join(lines)
        except RuntimeError as e:
            msg = str(e)
            if "not found" in msg.lower():
                return f"{msg}. Use scene_list_objects to verify the name."
            return msg

    return route_tool_call(
        tool_name="material_list_by_object",
        params={"object_name": object_name, "include_indices": include_indices},
        direct_executor=execute
    )


@mcp.tool()
def material_create(
    ctx: Context,
    name: str,
    base_color: Union[str, List[float], None] = None,
    metallic: float = 0.0,
    roughness: float = 0.5,
    emission_color: Union[str, List[float], None] = None,
    emission_strength: float = 0.0,
    alpha: float = 1.0,
) -> str:
    """
    [OBJECT MODE][SAFE] Creates a new PBR material with Principled BSDF.

    Workflow: AFTER → material_assign

    Args:
        name: Material name
        base_color: RGBA color [0-1] (default: [0.8, 0.8, 0.8, 1.0]). Accepts list or string "[r,g,b,a]".
        metallic: Metallic value 0-1
        roughness: Roughness value 0-1
        emission_color: Emission RGB [0-1]. Accepts list or string "[r,g,b]".
        emission_strength: Emission strength
        alpha: Alpha/opacity 0-1
    """
    def execute():
        handler = get_material_handler()
        try:
            parsed_base_color = parse_coordinate(base_color)
            parsed_emission_color = parse_coordinate(emission_color)
            result = handler.create_material(
                name=name,
                base_color=parsed_base_color,
                metallic=metallic,
                roughness=roughness,
                emission_color=parsed_emission_color,
                emission_strength=emission_strength,
                alpha=alpha,
            )
            ctx_info(ctx, f"Created material '{name}'")
            return result
        except (RuntimeError, ValueError) as e:
            return str(e)

    return route_tool_call(
        tool_name="material_create",
        params={
            "name": name,
            "base_color": base_color,
            "metallic": metallic,
            "roughness": roughness,
            "emission_color": emission_color,
            "emission_strength": emission_strength,
            "alpha": alpha
        },
        direct_executor=execute
    )


@mcp.tool()
def material_assign(
    ctx: Context,
    material_name: str,
    object_name: Optional[str] = None,
    slot_index: Optional[int] = None,
    assign_to_selection: bool = False,
) -> str:
    """
    [OBJECT MODE/EDIT MODE][SELECTION-BASED] Assigns material to object or selected faces.

    In Object Mode: Assigns material to entire object
    In Edit Mode with assign_to_selection=True: Assigns to selected faces only

    Workflow: BEFORE → material_create, mesh_select

    Args:
        material_name: Name of existing material
        object_name: Target object (default: active object)
        slot_index: Material slot index (default: auto)
        assign_to_selection: If True and in Edit Mode, assign to selected faces
    """
    def execute():
        handler = get_material_handler()
        try:
            result = handler.assign_material(
                material_name=material_name,
                object_name=object_name,
                slot_index=slot_index,
                assign_to_selection=assign_to_selection,
            )
            ctx_info(ctx, f"Assigned material '{material_name}'")
            return result
        except RuntimeError as e:
            msg = str(e)
            if "not found" in msg.lower():
                return f"{msg}. Use material_list to verify the material name."
            return msg

    return route_tool_call(
        tool_name="material_assign",
        params={
            "material_name": material_name,
            "object_name": object_name,
            "slot_index": slot_index,
            "assign_to_selection": assign_to_selection
        },
        direct_executor=execute
    )


@mcp.tool()
def material_set_params(
    ctx: Context,
    material_name: str,
    base_color: Optional[List[float]] = None,
    metallic: Optional[float] = None,
    roughness: Optional[float] = None,
    emission_color: Optional[List[float]] = None,
    emission_strength: Optional[float] = None,
    alpha: Optional[float] = None,
) -> str:
    """
    [OBJECT MODE][SAFE] Modifies parameters of existing material.

    Only provided parameters are changed; others remain unchanged.

    Workflow: BEFORE → material_list

    Args:
        material_name: Name of material to modify
        base_color: New RGBA color [0-1]
        metallic: New metallic value 0-1
        roughness: New roughness value 0-1
        emission_color: New emission RGB [0-1]
        emission_strength: New emission strength
        alpha: New alpha/opacity 0-1
    """
    def execute():
        handler = get_material_handler()
        try:
            result = handler.set_material_params(
                material_name=material_name,
                base_color=base_color,
                metallic=metallic,
                roughness=roughness,
                emission_color=emission_color,
                emission_strength=emission_strength,
                alpha=alpha,
            )
            ctx_info(ctx, f"Updated parameters for '{material_name}'")
            return result
        except RuntimeError as e:
            msg = str(e)
            if "not found" in msg.lower():
                return f"{msg}. Use material_list to verify the material name."
            return msg

    return route_tool_call(
        tool_name="material_set_params",
        params={
            "material_name": material_name,
            "base_color": base_color,
            "metallic": metallic,
            "roughness": roughness,
            "emission_color": emission_color,
            "emission_strength": emission_strength,
            "alpha": alpha
        },
        direct_executor=execute
    )


@mcp.tool()
def material_set_texture(
    ctx: Context,
    material_name: str,
    texture_path: str,
    input_name: str = "Base Color",
    color_space: str = "sRGB",
) -> str:
    """
    [OBJECT MODE][SAFE] Binds image texture to material input.

    Automatically creates Image Texture node and connects to Principled BSDF.

    Workflow: BEFORE → material_create

    Args:
        material_name: Target material name
        texture_path: Path to image file
        input_name: BSDF input ('Base Color', 'Roughness', 'Normal', 'Metallic', 'Emission Color')
        color_space: Color space ('sRGB' for color, 'Non-Color' for data maps)
    """
    def execute():
        handler = get_material_handler()
        try:
            result = handler.set_material_texture(
                material_name=material_name,
                texture_path=texture_path,
                input_name=input_name,
                color_space=color_space,
            )
            ctx_info(ctx, f"Connected texture to '{input_name}' on '{material_name}'")
            return result
        except RuntimeError as e:
            msg = str(e)
            if "not found" in msg.lower():
                return f"{msg}. Use material_list to verify the material name."
            return msg

    return route_tool_call(
        tool_name="material_set_texture",
        params={
            "material_name": material_name,
            "texture_path": texture_path,
            "input_name": input_name,
            "color_space": color_space
        },
        direct_executor=execute
    )


# TASK-045-6: material_inspect_nodes
@mcp.tool()
def material_inspect_nodes(
    ctx: Context,
    material_name: str,
    include_connections: bool = True,
) -> str:
    """
    [MATERIAL][SAFE][READ-ONLY] Inspects material shader node graph.

    Returns all nodes in the material's node tree with their types,
    parameters, and connections. Useful for understanding complex materials.

    Workflow: READ-ONLY | USE WITH → material_list, material_set_texture

    Args:
        material_name: Name of the material to inspect
        include_connections: Include node connections/links (default True)
    """
    def execute():
        handler = get_material_handler()
        try:
            result = handler.inspect_nodes(
                material_name=material_name,
                include_connections=include_connections,
            )

            # Format output for readability
            lines = [f"Material: {material_name}"]
            lines.append(f"Uses Nodes: {result.get('uses_nodes', False)}")

            nodes = result.get("nodes", [])
            lines.append(f"\nNodes ({len(nodes)}):")

            for node in nodes:
                node_name = node.get("name", "Unknown")
                node_type = node.get("type", "Unknown")
                lines.append(f"  • {node_name} ({node_type})")

                # Show key inputs with values
                inputs = node.get("inputs", [])
                if inputs:
                    for inp in inputs[:5]:  # Limit to first 5 inputs
                        inp_name = inp.get("name", "")
                        inp_value = inp.get("default_value")
                        is_linked = inp.get("is_linked", False)
                        if is_linked:
                            lines.append(f"      {inp_name}: [connected]")
                        elif inp_value is not None:
                            if isinstance(inp_value, list) and len(inp_value) >= 3:
                                # Format colors/vectors nicely
                                formatted = [round(v, 3) if isinstance(v, float) else v for v in inp_value]
                                lines.append(f"      {inp_name}: {formatted}")
                            else:
                                lines.append(f"      {inp_name}: {inp_value}")

            # Show connections if requested
            if include_connections:
                connections = result.get("connections", [])
                if connections:
                    lines.append(f"\nConnections ({len(connections)}):")
                    for conn in connections:
                        from_node = conn.get("from_node", "?")
                        from_socket = conn.get("from_socket", "?")
                        to_node = conn.get("to_node", "?")
                        to_socket = conn.get("to_socket", "?")
                        lines.append(f"  {from_node}.{from_socket} → {to_node}.{to_socket}")

            ctx_info(ctx, f"Inspected nodes for material '{material_name}'")
            return "\n".join(lines)
        except RuntimeError as e:
            msg = str(e)
            if "not found" in msg.lower():
                return f"{msg}. Use material_list to verify the material name."
            return msg

    return route_tool_call(
        tool_name="material_inspect_nodes",
        params={
            "material_name": material_name,
            "include_connections": include_connections
        },
        direct_executor=execute
    )
