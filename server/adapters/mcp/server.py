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
    """
    [SCENE][SAFE][READ-ONLY] Lists all objects in the current Blender scene with their types.
    """
    handler = get_scene_handler()
    try:
        result = handler.list_objects()
        ctx.info(f"Listed {len(result)} objects")
        return str(result)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def scene_delete_object(name: str, ctx: Context) -> str:
    """
    [SCENE][DESTRUCTIVE] Deletes an object from the scene by name.
    This permanently removes the object.
    
    Args:
        name: Name of the object to delete.
    """
    handler = get_scene_handler()
    try:
        return handler.delete_object(name)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def scene_clean_scene(ctx: Context, keep_lights_and_cameras: bool = True) -> str:
    """
    [SCENE][DESTRUCTIVE] Deletes objects from the scene.
    WARNING: If keep_lights_and_cameras=False, deletes EVERYTHING (hard reset).
    
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
    [SCENE][SAFE] Duplicates an object and optionally moves it.
    
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
    [SCENE][SAFE] Sets the active object.
    Important for operations that work on the "active" object (like adding modifiers).
    
    Args:
        name: Name of the object to set as active.
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
    [SCENE][SAFE][READ-ONLY] Gets a visual preview of the scene (OpenGL Viewport Render).
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
    [SCENE][SAFE] Creates a light source.

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
    [SCENE][SAFE] Creates a camera object.

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
    [SCENE][SAFE] Creates an Empty object (useful for grouping or tracking).

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
    [SCENE][SAFE] Sets the interaction mode (OBJECT, EDIT, SCULPT, POSE, WEIGHT_PAINT, TEXTURE_PAINT).
    
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

# ... Mesh Tools (Edit Mode) ...

from server.infrastructure.di import get_mesh_handler

@mcp.tool()
def mesh_select_all(ctx: Context, deselect: bool = False) -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Selects or deselects all geometry elements.
    
    Args:
        deselect: If True, deselects all. If False (default), selects all.
    """
    handler = get_mesh_handler()
    try:
        return handler.select_all(deselect)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_delete_selected(ctx: Context, type: str = 'VERT') -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Deletes selected geometry elements.
    
    Args:
        type: 'VERT', 'EDGE', 'FACE'.
    """
    handler = get_mesh_handler()
    try:
        return handler.delete_selected(type)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_select_by_index(ctx: Context, indices: List[int], type: str = 'VERT', selection_mode: str = 'SET') -> str:
    """
    [EDIT MODE][SELECTION-BASED][SAFE] Selects specific geometry elements by index.
    Uses BMesh for precise 0-based indexing.
    
    Args:
        indices: List of integer indices.
        type: 'VERT', 'EDGE', 'FACE'.
        selection_mode: 'SET' (replace), 'ADD' (extend), 'SUBTRACT' (deselect).
    """
    handler = get_mesh_handler()
    try:
        return handler.select_by_index(indices, type, selection_mode)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_extrude_region(ctx: Context, move: List[float] = None) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Extrudes selected geometry.
    WARNING: If 'move' is None, new geometry is created in-place (overlapping).
    Always provide 'move' vector or follow up with transform.
    
    Args:
        move: Optional [x, y, z] vector to move extruded region.
    """
    handler = get_mesh_handler()
    try:
        return handler.extrude_region(move)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_fill_holes(ctx: Context) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Fills holes by creating faces from selected edges/vertices.
    Equivalent to pressing 'F' key in Blender.
    """
    handler = get_mesh_handler()
    try:
        return handler.fill_holes()
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_bevel(
    ctx: Context,
    offset: float = 0.1,
    segments: int = 1,
    profile: float = 0.5,
    affect: str = 'EDGES'
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Bevels selected edges or vertices.
    
    Args:
        offset: Size of the bevel (distance/width).
        segments: Number of segments (rounding).
        profile: Shape of the bevel (0.5 is round).
        affect: 'EDGES' or 'VERTICES'.
    """
    handler = get_mesh_handler()
    try:
        return handler.bevel(offset, segments, profile, affect)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_loop_cut(
    ctx: Context,
    number_cuts: int = 1,
    smoothness: float = 0.0
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Adds cuts to mesh geometry.
    IMPORTANT: Uses 'subdivide' on SELECTED edges.
    Select edges perpendicular to desired cut direction first.
    
    Args:
        number_cuts: Number of cuts to make.
        smoothness: Smoothness of the subdivision.
    """
    handler = get_mesh_handler()
    try:
        return handler.loop_cut(number_cuts, smoothness)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_inset(
    ctx: Context,
    thickness: float = 0.0,
    depth: float = 0.0
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Insets selected faces (creates smaller faces inside).
    
    Args:
        thickness: Amount to inset.
        depth: Amount to move the inset face in/out.
    """
    handler = get_mesh_handler()
    try:
        return handler.inset(thickness, depth)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_boolean(
    ctx: Context,
    operation: str = 'DIFFERENCE',
    solver: str = 'FAST'
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Boolean operation on selected geometry.
    Formula: Unselected - Selected (for DIFFERENCE).
    TIP: For object-level booleans, prefer 'modeling_add_modifier(BOOLEAN)' (safer).
    
    Workflow:
      1. Select 'Cutter' geometry.
      2. Deselect 'Base' geometry.
      3. Run tool.
    
    Args:
        operation: 'INTERSECT', 'UNION', 'DIFFERENCE'.
        solver: 'FAST' or 'EXACT'.
    """
    handler = get_mesh_handler()
    try:
        return handler.boolean(operation, solver)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_merge_by_distance(
    ctx: Context,
    distance: float = 0.001
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Merges vertices within threshold distance.
    Useful for cleaning up geometry after imports or boolean ops.
    
    Args:
        distance: Threshold distance to merge.
    """
    handler = get_mesh_handler()
    try:
        return handler.merge_by_distance(distance)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def mesh_subdivide(
    ctx: Context,
    number_cuts: int = 1,
    smoothness: float = 0.0
) -> str:
    """
    [EDIT MODE][SELECTION-BASED][DESTRUCTIVE] Subdivides selected geometry.
    
    Args:
        number_cuts: Number of cuts.
        smoothness: Smoothness factor (0.0 to 1.0).
    """
    handler = get_mesh_handler()
    try:
        return handler.subdivide(number_cuts, smoothness)
    except RuntimeError as e:
        return str(e)

def run():
    """Starts the MCP server."""
    mcp.run()