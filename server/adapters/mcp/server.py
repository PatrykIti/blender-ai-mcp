from fastmcp import FastMCP, Context
from typing import List, Dict, Any, Optional
from server.infrastructure.di import get_scene_handler, get_modeling_handler

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

def run():
    """Starts the MCP server."""
    mcp.run()