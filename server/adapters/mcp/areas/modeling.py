from typing import Any, Dict, List, Optional, Union
from fastmcp import Context
from server.adapters.mcp.instance import mcp
from server.adapters.mcp.utils import parse_coordinate, parse_dict
from server.adapters.mcp.router_helper import route_tool_call
from server.infrastructure.di import get_modeling_handler

@mcp.tool()
def modeling_create_primitive(
    ctx: Context,
    primitive_type: str,
    radius: float = 1.0,
    size: float = 2.0,
    location: Union[str, List[float]] = [0.0, 0.0, 0.0],
    rotation: Union[str, List[float]] = [0.0, 0.0, 0.0],
    name: str = None
) -> str:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Creates a 3D primitive object.

    Workflow: START → new object | AFTER → modeling_transform, scene_set_mode('EDIT')

    Args:
        primitive_type: "Cube", "Sphere", "Cylinder", "Plane", "Cone", "Monkey", "Torus".
        radius: Radius for Sphere/Cylinder/Cone.
        size: Size for Cube/Plane/Monkey.
        location: [x, y, z] coordinates. Can be a list [0.0, 0.0, 0.0] or string '[0.0, 0.0, 0.0]'.
        rotation: [rx, ry, rz] rotation in radians. Can be a list or string.
        name: Optional name for the new object.
    """
    def execute():
        handler = get_modeling_handler()
        try:
            parsed_location = parse_coordinate(location) or [0.0, 0.0, 0.0]
            parsed_rotation = parse_coordinate(rotation) or [0.0, 0.0, 0.0]
            return handler.create_primitive(primitive_type, radius, size, parsed_location, parsed_rotation, name)
        except (RuntimeError, ValueError) as e:
            return str(e)

    return route_tool_call(
        tool_name="modeling_create_primitive",
        params={"primitive_type": primitive_type, "radius": radius, "size": size, "location": location, "rotation": rotation, "name": name},
        direct_executor=execute
    )

@mcp.tool()
def modeling_transform_object(
    ctx: Context,
    name: str,
    location: Union[str, List[float], None] = None,
    rotation: Union[str, List[float], None] = None,
    scale: Union[str, List[float], None] = None
) -> str:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Transforms (move, rotate, scale) an existing object.

    Workflow: AFTER → modeling_create_primitive | BEFORE → scene_set_mode('EDIT')

    Args:
        name: Name of the object.
        location: New [x, y, z] coordinates (optional). Can be a list [0.0, 0.0, 2.0] or string '[0.0, 0.0, 2.0]'.
        rotation: New [rx, ry, rz] rotation in radians (optional). Can be a list or string.
        scale: New [sx, sy, sz] scale factors (optional). Can be a list or string.
    """
    def execute():
        handler = get_modeling_handler()
        try:
            parsed_location = parse_coordinate(location)
            parsed_rotation = parse_coordinate(rotation)
            parsed_scale = parse_coordinate(scale)
            return handler.transform_object(name, parsed_location, parsed_rotation, parsed_scale)
        except (RuntimeError, ValueError) as e:
            return str(e)

    return route_tool_call(
        tool_name="modeling_transform_object",
        params={"name": name, "location": location, "rotation": rotation, "scale": scale},
        direct_executor=execute
    )

@mcp.tool()
def modeling_add_modifier(
    ctx: Context,
    name: str,
    modifier_type: str,
    properties: Union[str, Dict[str, Any], None] = None
) -> str:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Adds a modifier to an object.
    Preferred method for booleans, subdivision, mirroring (non-destructive stack).

    Workflow: NON-DESTRUCTIVE | AFTER → modeling_apply_modifier | ALT TO → mesh_boolean

    Args:
        name: Object name.
        modifier_type: Type of modifier (e.g., 'SUBSURF', 'BEVEL', 'MIRROR', 'BOOLEAN').
        properties: Dictionary of modifier properties to set (e.g., {'levels': 2}). Can be a dict or string '{"levels": 2}'.
            BOOLEAN note: to set the cutter/target object, pass `{"object": "<ObjectName>"}` (or alias `object_name`)
            where the value is the name of an existing Blender object.
    """
    def execute():
        handler = get_modeling_handler()
        try:
            parsed_properties = parse_dict(properties)
            return handler.add_modifier(name, modifier_type, parsed_properties)
        except (RuntimeError, ValueError) as e:
            return str(e)

    return route_tool_call(
        tool_name="modeling_add_modifier",
        params={"name": name, "modifier_type": modifier_type, "properties": properties},
        direct_executor=execute
    )

@mcp.tool()
def modeling_apply_modifier(
    ctx: Context,
    name: str, 
    modifier_name: str
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Applies a modifier, making its changes permanent to the mesh.

    Workflow: BEFORE → modeling_list_modifiers | DESTRUCTIVE - bakes changes

    Args:
        name: Object name.
        modifier_name: The name of the modifier to apply.
    """
    return route_tool_call(
        tool_name="modeling_apply_modifier",
        params={"name": name, "modifier_name": modifier_name},
        direct_executor=lambda: get_modeling_handler().apply_modifier(name, modifier_name)
    )

@mcp.tool()
def modeling_convert_to_mesh(
    ctx: Context,
    name: str
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Converts a non-mesh object (Curve, Text, Surface) to a mesh.

    Workflow: USE FOR → Curve/Text → Mesh | AFTER → scene_set_mode('EDIT')

    Args:
        name: The name of the object to convert.
    """
    return route_tool_call(
        tool_name="modeling_convert_to_mesh",
        params={"name": name},
        direct_executor=lambda: get_modeling_handler().convert_to_mesh(name)
    )

@mcp.tool()
def modeling_join_objects(
    ctx: Context,
    object_names: List[str]
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Joins multiple mesh objects into a single mesh.
    IMPORTANT: The LAST object in the list becomes the Active Object (Base).

    Workflow: BEFORE → mesh_boolean workflow | AFTER → mesh_select_linked

    Args:
        object_names: A list of names of the objects to join.
    """
    return route_tool_call(
        tool_name="modeling_join_objects",
        params={"object_names": object_names},
        direct_executor=lambda: get_modeling_handler().join_objects(object_names)
    )

@mcp.tool()
def modeling_separate_object(
    ctx: Context,
    name: str,
    type: str = "LOOSE"
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Separates a mesh into new objects (LOOSE, SELECTED, MATERIAL).

    Workflow: AFTER → mesh_select_linked | USE → split mesh islands

    Args:
        name: The name of the object to separate.
        type: The separation method: "LOOSE", "SELECTED", or "MATERIAL".
    """
    def execute():
        handler = get_modeling_handler()
        try:
            result = handler.separate_object(name, type)
            return str(result)
        except RuntimeError as e:
            return str(e)

    return route_tool_call(
        tool_name="modeling_separate_object",
        params={"name": name, "type": type},
        direct_executor=execute
    )

@mcp.tool()
def modeling_list_modifiers(
    ctx: Context,
    name: str
) -> str:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Lists all modifiers currently on the specified object.

    Workflow: READ-ONLY | BEFORE → modeling_apply_modifier

    Args:
        name: The name of the object.
    """
    def execute():
        handler = get_modeling_handler()
        try:
            modifiers = handler.get_modifiers(name)
            return str(modifiers)
        except RuntimeError as e:
            return str(e)

    return route_tool_call(
        tool_name="modeling_list_modifiers",
        params={"name": name},
        direct_executor=execute
    )


# Internal function - exposed via modeling_get_modifier_data and scene_inspect
def _modeling_get_modifier_data(
    ctx: Context,
    object_name: str,
    modifier_name: Optional[str] = None,
    include_node_tree: bool = False
) -> str:
    """
    [OBJECT MODE][READ-ONLY][SAFE] Returns full modifier properties.
    """
    handler = get_modeling_handler()
    try:
        import json
        data = handler.get_modifier_data(object_name, modifier_name, include_node_tree)
        return json.dumps(data, indent=2)
    except RuntimeError as e:
        return str(e)


@mcp.tool()
def modeling_get_modifier_data(
    ctx: Context,
    object_name: str,
    modifier_name: Optional[str] = None,
    include_node_tree: bool = False
) -> str:
    """
    [OBJECT MODE][READ-ONLY][SAFE] Returns full modifier properties.

    Workflow: READ-ONLY | USE → reconstruction of modifier stacks

    Args:
        object_name: Name of the object to inspect
        modifier_name: Optional modifier name filter (default: all)
        include_node_tree: Include Geometry Nodes group metadata (default: False)

    Returns:
        JSON string with modifier properties and object references.
    """
    return route_tool_call(
        tool_name="modeling_get_modifier_data",
        params={
            "object_name": object_name,
            "modifier_name": modifier_name,
            "include_node_tree": include_node_tree
        },
        direct_executor=lambda: _modeling_get_modifier_data(
            ctx,
            object_name,
            modifier_name,
            include_node_tree
        )
    )

@mcp.tool()
def modeling_set_origin(
    ctx: Context,
    name: str,
    type: str
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Sets the origin point of an object.

    Workflow: AFTER → geometry changes | BEFORE → modeling_transform

    Args:
        name: Object name.
        type: Origin type (e.g., 'ORIGIN_GEOMETRY', 'ORIGIN_CURSOR', 'ORIGIN_CENTER_OF_MASS').
    """
    return route_tool_call(
        tool_name="modeling_set_origin",
        params={"name": name, "type": type},
        direct_executor=lambda: get_modeling_handler().set_origin(name, type)
    )


# ==============================================================================
# TASK-038-1: Metaball Tools
# ==============================================================================


@mcp.tool()
def metaball_create(
    ctx: Context,
    name: str = "Metaball",
    location: Union[str, List[float], None] = None,
    element_type: str = "BALL",
    radius: float = 1.0,
    resolution: float = 0.2,
    threshold: float = 0.6,
) -> str:
    """
    [OBJECT MODE][SCENE] Creates a metaball object.

    Metaballs automatically merge when close together, creating organic blob shapes.
    Perfect for: veins, tumors, fat deposits, cellular structures, organs.

    Element types:
        - BALL: Spherical element (default)
        - CAPSULE: Tubular element for blood vessels
        - PLANE: Flat disc element
        - ELLIPSOID: Stretched sphere
        - CUBE: Cubic element

    Workflow: AFTER → metaball_add_element | metaball_to_mesh

    Args:
        name: Name for the metaball object
        location: World position [x, y, z]
        element_type: BALL, CAPSULE, PLANE, ELLIPSOID, CUBE
        radius: Initial element radius (default 1.0)
        resolution: Surface resolution - lower = higher quality (default 0.2)
        threshold: Merge threshold for elements (default 0.6)

    Examples:
        metaball_create(name="Heart", element_type="ELLIPSOID", radius=1.5)
        metaball_create(name="Tumor", resolution=0.1) -> Higher quality
    """
    def execute():
        handler = get_modeling_handler()
        try:
            parsed_location = parse_coordinate(location)
            return handler.metaball_create(
                name=name,
                location=parsed_location,
                element_type=element_type,
                radius=radius,
                resolution=resolution,
                threshold=threshold,
            )
        except RuntimeError as e:
            return str(e)

    return route_tool_call(
        tool_name="metaball_create",
        params={"name": name, "location": location, "element_type": element_type, "radius": radius, "resolution": resolution, "threshold": threshold},
        direct_executor=execute
    )


@mcp.tool()
def metaball_add_element(
    ctx: Context,
    metaball_name: str,
    element_type: str = "BALL",
    location: Union[str, List[float], None] = None,
    radius: float = 1.0,
    stiffness: float = 2.0,
) -> str:
    """
    [OBJECT MODE] Adds element to existing metaball.

    Multiple elements merge together based on proximity and stiffness.
    Use CAPSULE for tubular structures (blood vessels, nerves).

    Workflow: BEFORE → metaball_create | AFTER → metaball_to_mesh

    Args:
        metaball_name: Name of target metaball object
        element_type: BALL, CAPSULE, PLANE, ELLIPSOID, CUBE
        location: Position relative to metaball origin [x, y, z]
        radius: Element radius (default 1.0)
        stiffness: How strongly it merges with other elements (default 2.0)

    Examples:
        metaball_add_element("Heart", location=[0.5, 0, 0.3], radius=0.8)
        metaball_add_element("Vessel", element_type="CAPSULE", radius=0.2)
    """
    def execute():
        handler = get_modeling_handler()
        try:
            parsed_location = parse_coordinate(location)
            return handler.metaball_add_element(
                metaball_name=metaball_name,
                element_type=element_type,
                location=parsed_location,
                radius=radius,
                stiffness=stiffness,
            )
        except RuntimeError as e:
            return str(e)

    return route_tool_call(
        tool_name="metaball_add_element",
        params={"metaball_name": metaball_name, "element_type": element_type, "location": location, "radius": radius, "stiffness": stiffness},
        direct_executor=execute
    )


@mcp.tool()
def metaball_to_mesh(
    ctx: Context,
    metaball_name: str,
    apply_resolution: bool = True,
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Converts metaball to mesh.

    Required for:
    - Mesh editing operations (extrude, bevel, etc.)
    - Export to game engines
    - Further sculpting with dyntopo

    Workflow: AFTER → sculpt_enable_dyntopo | mesh_remesh_voxel (cleanup)

    Args:
        metaball_name: Name of metaball to convert
        apply_resolution: Whether to apply current resolution (default True)

    Examples:
        metaball_to_mesh("Heart") -> Converts to mesh for editing
    """
    return route_tool_call(
        tool_name="metaball_to_mesh",
        params={"metaball_name": metaball_name, "apply_resolution": apply_resolution},
        direct_executor=lambda: get_modeling_handler().metaball_to_mesh(metaball_name=metaball_name, apply_resolution=apply_resolution)
    )


# ==============================================================================
# TASK-038-6: Skin Modifier Workflow
# ==============================================================================


@mcp.tool()
def skin_create_skeleton(
    ctx: Context,
    name: str = "Skeleton",
    vertices: Union[str, List[List[float]], None] = None,
    edges: Union[str, List[List[int]], None] = None,
    location: Union[str, List[float], None] = None,
) -> str:
    """
    [OBJECT MODE][SCENE] Creates skeleton mesh for Skin modifier.

    Define vertices as path points, edges connect them.
    Skin modifier will create tubular mesh around this skeleton.

    Use case: blood vessels, nerves, tree branches, tentacles.

    Workflow: AFTER → modeling_add_modifier(type="SKIN") | skin_set_radius

    Args:
        name: Name for skeleton object (default "Skeleton")
        vertices: List of vertex positions [[x,y,z], ...] (default [[0,0,0], [0,0,1]])
        edges: List of edge connections [[v1, v2], ...] (auto-connect sequentially if None)
        location: World position [x, y, z]

    Examples:
        skin_create_skeleton(name="Artery", vertices=[[0,0,0], [0,0,1], [0.3,0,1.5]])
        skin_create_skeleton(name="Branch", vertices=[[0,0,0], [0,0,1], [0.5,0,1.5], [-0.5,0,1.5]], edges=[[0,1], [1,2], [1,3]])
    """
    def execute():
        handler = get_modeling_handler()
        try:
            parsed_location = parse_coordinate(location)
            parsed_vertices = parse_coordinate(vertices) if isinstance(vertices, str) else vertices
            parsed_edges = parse_coordinate(edges) if isinstance(edges, str) else edges
            return handler.skin_create_skeleton(
                name=name,
                vertices=parsed_vertices,
                edges=parsed_edges,
                location=parsed_location,
            )
        except RuntimeError as e:
            return str(e)

    return route_tool_call(
        tool_name="skin_create_skeleton",
        params={"name": name, "vertices": vertices, "edges": edges, "location": location},
        direct_executor=execute
    )


@mcp.tool()
def skin_set_radius(
    ctx: Context,
    object_name: str,
    vertex_index: Optional[int] = None,
    radius_x: float = 0.25,
    radius_y: float = 0.25,
) -> str:
    """
    [EDIT MODE] Sets skin radius at vertices.

    Each vertex can have different X/Y radius for elliptical cross-sections.

    Use case: Varying vessel thickness (aorta thicker than capillaries).

    Workflow: BEFORE → skin_create_skeleton | AFTER → modeling_apply_modifier

    Args:
        object_name: Name of object with skin modifier
        vertex_index: Specific vertex index (None = all selected/all vertices)
        radius_x: X radius for elliptical cross-section (default 0.25)
        radius_y: Y radius for elliptical cross-section (default 0.25)

    Examples:
        skin_set_radius("Artery", vertex_index=0, radius_x=0.15) -> Thick at base
        skin_set_radius("Artery", radius_x=0.05, radius_y=0.05) -> Thin everywhere
    """
    return route_tool_call(
        tool_name="skin_set_radius",
        params={"object_name": object_name, "vertex_index": vertex_index, "radius_x": radius_x, "radius_y": radius_y},
        direct_executor=lambda: get_modeling_handler().skin_set_radius(object_name=object_name, vertex_index=vertex_index, radius_x=radius_x, radius_y=radius_y)
    )
