from fastmcp import FastMCP, Context
from server.infrastructure.di import get_scene_handler

# Initialize MCP Server
mcp = FastMCP("blender-ai-mcp", dependencies=["pydantic", "fastmcp"])

# --- Tool Definitions (Adapter Layer) ---

@mcp.tool()
def list_objects(ctx: Context) -> str:
    """List all objects in the current Blender scene with their types."""
    # Injection: Get handler from DI provider
    # (W przyszłości FastMCP może wspierać 'Depends(get_scene_handler)', na razie robimy manual call)
    handler = get_scene_handler()
    
    try:
        result = handler.list_objects()
        ctx.info(f"Listed {len(result)} objects") # Logowanie do kontekstu MCP
        return str(result)
    except RuntimeError as e:
        ctx.error(f"Error listing objects: {e}")
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

def run():
    """Starts the MCP server."""
    mcp.run()