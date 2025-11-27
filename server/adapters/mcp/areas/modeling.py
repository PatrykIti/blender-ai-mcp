from typing import Any, Dict, List, Optional
from fastmcp import Context
from server.adapters.mcp.instance import mcp
from server.infrastructure.di import get_modeling_handler

@mcp.tool()
def modeling_create_primitive(
    ctx: Context,
    primitive_type: str, 
    radius: float = 1.0, 
    size: float = 2.0, 
    location: List[float] = (0.0, 0.0, 0.0), 
    rotation: List[float] = (0.0, 0.0, 0.0),
    name: str = None
) -> str:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Creates a 3D primitive object.
    
    Args:
        primitive_type: "Cube", "Sphere", "Cylinder", "Plane", "Cone", "Monkey", "Torus".
        radius: Radius for Sphere/Cylinder/Cone.
        size: Size for Cube/Plane/Monkey.
        location: [x, y, z] coordinates.
        rotation: [rx, ry, rz] rotation in radians.
        name: Optional name for the new object.
    """
    handler = get_modeling_handler()
    try:
        return handler.create_primitive(primitive_type, radius, size, location, rotation, name)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def modeling_transform_object(
    ctx: Context,
    name: str, 
    location: Optional[List[float]] = None, 
    rotation: Optional[List[float]] = None, 
    scale: Optional[List[float]] = None
) -> str:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Transforms (move, rotate, scale) an existing object.
    
    Args:
        name: Name of the object.
        location: New [x, y, z] coordinates (optional).
        rotation: New [rx, ry, rz] rotation in radians (optional).
        scale: New [sx, sy, sz] scale factors (optional).
    """
    handler = get_modeling_handler()
    try:
        return handler.transform_object(name, location, rotation, scale)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def modeling_add_modifier(
    ctx: Context,
    name: str, 
    modifier_type: str, 
    properties: Dict[str, Any] = None
) -> str:
    """
    [OBJECT MODE][SAFE][NON-DESTRUCTIVE] Adds a modifier to an object.
    Preferred method for booleans, subdivision, mirroring (non-destructive stack).
    
    Args:
        name: Object name.
        modifier_type: Type of modifier (e.g., 'SUBSURF', 'BEVEL', 'MIRROR', 'BOOLEAN').
        properties: Dictionary of modifier properties to set (e.g., {'levels': 2}).
    """
    handler = get_modeling_handler()
    try:
        return handler.add_modifier(name, modifier_type, properties)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def modeling_apply_modifier(
    ctx: Context,
    name: str, 
    modifier_name: str
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Applies a modifier, making its changes permanent to the mesh.
    
    Args:
        name: Object name.
        modifier_name: The name of the modifier to apply.
    """
    handler = get_modeling_handler()
    try:
        return handler.apply_modifier(name, modifier_name)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def modeling_convert_to_mesh(
    ctx: Context,
    name: str
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Converts a non-mesh object (Curve, Text, Surface) to a mesh.
    
    Args:
        name: The name of the object to convert.
    """
    handler = get_modeling_handler()
    try:
        return handler.convert_to_mesh(name)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def modeling_join_objects(
    ctx: Context,
    object_names: List[str]
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Joins multiple mesh objects into a single mesh.
    IMPORTANT: The LAST object in the list becomes the Active Object (Base).
    
    Args:
        object_names: A list of names of the objects to join.
    """
    handler = get_modeling_handler()
    try:
        return handler.join_objects(object_names)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def modeling_separate_object(
    ctx: Context,
    name: str,
    type: str = "LOOSE"
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Separates a mesh into new objects (LOOSE, SELECTED, MATERIAL).
    
    Args:
        name: The name of the object to separate.
        type: The separation method: "LOOSE", "SELECTED", or "MATERIAL".
    """
    handler = get_modeling_handler()
    try:
        result = handler.separate_object(name, type)
        return str(result)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def modeling_list_modifiers(
    ctx: Context,
    name: str
) -> str:
    """
    [OBJECT MODE][SAFE][READ-ONLY] Lists all modifiers currently on the specified object.
    
    Args:
        name: The name of the object.
    """
    handler = get_modeling_handler()
    try:
        modifiers = handler.get_modifiers(name)
        return str(modifiers)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def modeling_set_origin(
    ctx: Context,
    name: str,
    type: str
) -> str:
    """
    [OBJECT MODE][DESTRUCTIVE] Sets the origin point of an object.
    
    Args:
        name: Object name.
        type: Origin type (e.g., 'ORIGIN_GEOMETRY', 'ORIGIN_CURSOR', 'ORIGIN_CENTER_OF_MASS').
    """
    handler = get_modeling_handler()
    try:
        return handler.set_origin(name, type)
    except RuntimeError as e:
        return str(e)