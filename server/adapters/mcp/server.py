from fastmcp import FastMCP, Context, Image
from typing import List, Dict, Any, Optional
from server.infrastructure.di import get_scene_handler, get_modeling_handler
import base64

# Initialize MCP Server
mcp = FastMCP("blender-ai-mcp", dependencies=["pydantic", "fastmcp"])

# --- Tool Definitions (Adapter Layer) ---

# ... Scene Tools ...
@mcp.tool()
def scene_list_objects(ctx: Context) -> str:
    """List all objects in the current Blender scene with their types."""
    handler = get_scene_handler()
    try:
        result = handler.list_objects()
        ctx.info(f"Listed {len(result)} objects")
        return str(result)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def scene_delete_object(name: str, ctx: Context) -> str:
    """Delete an object from the scene by name."""
    handler = get_scene_handler()
    try:
        return handler.delete_object(name)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def scene_clean_scene(ctx: Context, keep_lights_and_cameras: bool = True) -> str:
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
def scene_duplicate_object(ctx: Context, name: str, translation: List[float] = None) -> str:
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
def scene_set_active_object(ctx: Context, name: str) -> str:
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
def scene_get_viewport(
    ctx: Context, 
    width: int = 1024, 
    height: int = 768, 
    shading: str = "SOLID", 
    camera_name: str = None, 
    focus_target: str = None
) -> Image:
    """
    Get a visual preview of the scene (OpenGL Viewport Render).
    Returns an Image resource that the AI can see.

    Args:
        width: Image width.
        height: Image height.
        shading: Viewport shading mode ('WIREFRAME', 'SOLID', 'MATERIAL', 'RENDERED').
        camera_name: Name of the camera to use. If None or "USER_PERSPECTIVE", uses a temporary camera.
        focus_target: Name of the object to focus on. Only works if camera_name is None/"USER_PERSPECTIVE".
    """
    handler = get_scene_handler()
    try:
        # Returns base64 string
        b64_data = handler.get_viewport(width, height, shading, camera_name, focus_target)
        # Convert to bytes for FastMCP Image
        image_bytes = base64.b64decode(b64_data)
        return Image(data=image_bytes, format="jpeg")
    except RuntimeError as e:
        raise e

@mcp.tool()
def scene_create_light(
    ctx: Context,
    type: str,
    energy: float = 1000.0,
    color: List[float] = (1.0, 1.0, 1.0),
    location: List[float] = (0.0, 0.0, 5.0),
    name: Optional[str] = None
) -> str:
    """
    Create a light source.

    Args:
        type: 'POINT', 'SUN', 'SPOT', 'AREA'.
        energy: Power in Watts.
        color: [r, g, b] (0.0 to 1.0).
        location: [x, y, z].
        name: Optional custom name.
    """
    handler = get_scene_handler()
    try:
        return handler.create_light(type, energy, color, location, name)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def scene_create_camera(
    ctx: Context,
    location: List[float],
    rotation: List[float],
    lens: float = 50.0,
    clip_start: Optional[float] = None,
    clip_end: Optional[float] = None,
    name: Optional[str] = None
) -> str:
    """
    Create a camera object.

    Args:
        location: [x, y, z].
        rotation: [x, y, z] Euler angles in radians.
        lens: Focal length in mm.
        clip_start: Near clipping distance.
        clip_end: Far clipping distance.
        name: Optional custom name.
    """
    handler = get_scene_handler()
    try:
        return handler.create_camera(location, rotation, lens, clip_start, clip_end, name)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def scene_create_empty(
    ctx: Context,
    type: str,
    size: float = 1.0,
    location: List[float] = (0.0, 0.0, 0.0),
    name: Optional[str] = None
) -> str:
    """
    Create an Empty object (useful for grouping or tracking).

    Args:
        type: 'PLAIN_AXES', 'ARROWS', 'SINGLE_ARROW', 'CIRCLE', 'CUBE', 'SPHERE', 'CONE', 'IMAGE'.
        size: Display size.
        location: [x, y, z].
        name: Optional custom name.
    """
    handler = get_scene_handler()
    try:
        return handler.create_empty(type, size, location, name)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def scene_set_mode(ctx: Context, mode: str) -> str:
    """
    Set the interaction mode (OBJECT, EDIT, SCULPT, POSE, WEIGHT_PAINT, TEXTURE_PAINT).
    
    Args:
        mode: The target mode (case-insensitive).
    """
    handler = get_scene_handler()
    try:
        return handler.set_mode(mode)
    except RuntimeError as e:
        return str(e)

# ... Modeling Tools ...

@mcp.tool()
def modeling_create_primitive(
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
def modeling_transform_object(
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
def modeling_add_modifier(
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
def modeling_apply_modifier(
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
def modeling_convert_to_mesh(
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
def modeling_join_objects(
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
def modeling_separate_object(
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
def modeling_list_modifiers(
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
def modeling_set_origin(
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

# ... Mesh Tools (Edit Mode) ...

from server.infrastructure.di import get_mesh_handler

@mcp.tool()
def mesh_select_all(ctx: Context, deselect: bool = False) -> str:
    """
    Selects or deselects all geometry elements in Edit Mode.
    Ensures the active object is in Edit Mode.
    """
    handler = get_mesh_handler()
    try:
        return handler.select_all(deselect)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_delete_selected(ctx: Context, type: str = 'VERT') -> str:
    """
    Deletes selected geometry elements.
    Type: 'VERT', 'EDGE', 'FACE'.
    """
    handler = get_mesh_handler()
    try:
        return handler.delete_selected(type)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_select_by_index(ctx: Context, indices: List[int], type: str = 'VERT', deselect: bool = False) -> str:
    """
    Selects specific geometry elements by their index.
    Useful for AI to target specific parts of the mesh.
    """
    handler = get_mesh_handler()
    try:
        return handler.select_by_index(indices, type, deselect)
    except RuntimeError as e:
        return str(e)

def run():
    """Starts the MCP server."""
    mcp.run()