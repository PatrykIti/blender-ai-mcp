from fastmcp import FastMCP, Context, Image
from typing import List, Dict, Any, Optional
from server.infrastructure.di import get_scene_handler, get_modeling_handler
import base64

# Initialize MCP Server
mcp = FastMCP("blender-ai-mcp", dependencies=["pydantic", "fastmcp"])

# --- Tool Definitions (Adapter Layer) ---

# ... Scene Tools ...
@mcp.tool()
def list_objects(ctx: Context) -> str:
    """List all objects in the current Blender scene with their types."""
    handler = get_scene_handler()
    try:
        result = handler.list_objects()
        ctx.info(f"Listed {len(result)} objects")
        return str(result)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def delete_object(name: str, ctx: Context) -> str:
    """Delete an object from the scene by name."""
    handler = get_scene_handler()
    try:
        return handler.delete_object(name)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def clean_scene(ctx: Context, keep_lights_and_cameras: bool = True) -> str:
    """
    Delete objects from the scene.
    
    Args:
        keep_lights_and_cameras: If True (default), keeps Lights and Cameras. 
                                 If False, deletes EVERYTHING (hard reset).
    """
    handler = get_scene_handler()
    try:
        return handler.clean_scene(keep_lights_and_cameras)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def duplicate_object(ctx: Context, name: str, translation: List[float] = None) -> str:
    """
    Duplicate an object and optionally move it.
    
    Args:
        name: Name of the object to duplicate.
        translation: Optional [x, y, z] vector to move the copy.
    """
    handler = get_scene_handler()
    try:
        return str(handler.duplicate_object(name, translation))
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def set_active_object(ctx: Context, name: str) -> str:
    """
    Set the active object. 
    This is important for operations that work on the "active" object (like adding modifiers).
    """
    handler = get_scene_handler()
    try:
        return handler.set_active_object(name)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def get_viewport(ctx: Context, width: int = 1024, height: int = 768) -> Image:
    """
    Get a visual preview of the scene (OpenGL Viewport Render).
    Returns an Image resource that the AI can see.
    """
    handler = get_scene_handler()
    try:
        # Returns base64 string
        b64_data = handler.get_viewport(width, height)
        # Convert to bytes for FastMCP Image
        image_bytes = base64.b64decode(b64_data)
        return Image(data=image_bytes, format="jpeg")
    except RuntimeError as e:
        raise e

# ... Modeling Tools ...

@mcp.tool()
def create_primitive(
    ctx: Context,
    primitive_type: str, 
    radius: float = 1.0, 
    size: float = 2.0, 
    location: List[float] = (0.0, 0.0, 0.0), 
    rotation: List[float] = (0.0, 0.0, 0.0)
) -> str:
    """
    Create a 3D primitive.
    
    Args:
        primitive_type: "Cube", "Sphere", "Cylinder", "Plane", "Cone", "Monkey", "Torus".
        radius: Radius for Sphere/Cylinder/Cone.
        size: Size for Cube/Plane/Monkey.
        location: [x, y, z] coordinates.
        rotation: [rx, ry, rz] rotation in radians.
    """
    handler = get_modeling_handler()
    try:
        return handler.create_primitive(primitive_type, radius, size, location, rotation)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def transform_object(
    ctx: Context,
    name: str, 
    location: Optional[List[float]] = None, 
    rotation: Optional[List[float]] = None, 
    scale: Optional[List[float]] = None
) -> str:
    """
    Transform (move, rotate, scale) an existing object.
    
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
def add_modifier(
    ctx: Context,
    name: str, 
    modifier_type: str, 
    properties: Dict[str, Any] = None
) -> str:
    """
    Add a modifier to an object.
    
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
def apply_modifier(
    ctx: Context,
    name: str, 
    modifier_name: str
) -> str:
    """
    Applies a modifier to an object, making its changes permanent to the mesh.
    
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
def convert_to_mesh(
    ctx: Context,
    name: str
) -> str:
    """
    Converts a non-mesh object (e.g., Curve, Text, Surface) to a mesh.
    
    Args:
        name: The name of the object to convert.
    """
    handler = get_modeling_handler()
    try:
        return handler.convert_to_mesh(name)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def join_objects(
    ctx: Context,
    object_names: List[str]
) -> str:
    """
    Joins multiple mesh objects into a single mesh object.
    
    Args:
        object_names: A list of names of the objects to join.
    """
    handler = get_modeling_handler()
    try:
        return handler.join_objects(object_names)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def separate_object(
    ctx: Context,
    name: str,
    type: str = "LOOSE"
) -> str:
    """
    Separates a mesh object into new objects based on type (LOOSE, SELECTED, MATERIAL).
    
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
def separate_object(
    ctx: Context,
    name: str,
    type: str = "LOOSE"
) -> List[str]:
    """
    Separates a mesh object into new objects based on type (LOOSE, SELECTED, MATERIAL).
    
    Args:
        name: The name of the object to separate.
        type: The separation method: "LOOSE", "SELECTED", or "MATERIAL".
    """
    handler = get_modeling_handler()
    try:
        return handler.separate_object(name, type)["separated_objects"]
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def list_modifiers(
    ctx: Context,
    name: str
) -> str:
    """
    Lists all modifiers currently on the specified object.
    
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
def set_origin(
    ctx: Context,
    name: str,
    type: str
) -> str:
    """
    Sets the origin point of an object using Blender's origin_set operator types.
    Examples for 'type': 'ORIGIN_GEOMETRY_TO_CURSOR', 'ORIGIN_CURSOR_TO_GEOMETRY', 'ORIGIN_GEOMETRY_TO_MASS'.
    """
    handler = get_modeling_handler()
    try:
        return handler.set_origin(name, type)
    except RuntimeError as e:
        return str(e)

def run():
    """Starts the MCP server."""
    mcp.run()