from fastmcp import FastMCP
from server.infrastructure.container import get_container

# Get pre-wired handlers from DI container
container = get_container()

# Initialize MCP Server
mcp = FastMCP("blender-ai-mcp", dependencies=["pydantic", "fastmcp"])

# --- Tool Definitions (Adapter Layer) ---

@mcp.tool()
def list_objects() -> str:
    """List all objects in the current Blender scene with their types."""
    try:
        result = container.scene_handler.list_objects()
        return str(result)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def delete_object(name: str) -> str:
    """Delete an object from the scene by name."""
    try:
        return container.scene_handler.delete_object(name)
    except RuntimeError as e:
        return str(e)

@mcp.tool()
def clean_scene(keep_lights_and_cameras: bool = True) -> str:
    """
    Delete objects from the scene.
    
    Args:
        keep_lights_and_cameras: If True (default), keeps Lights and Cameras. 
                                 If False, deletes EVERYTHING (hard reset).
    """
    try:
        return container.scene_handler.clean_scene(keep_lights_and_cameras)
    except RuntimeError as e:
        return str(e)

def run():
    """Starts the MCP server."""
    mcp.run()
