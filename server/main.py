from fastmcp import FastMCP
from server.adapters.rpc.client import RpcClient

# Initialize FastMCP Server
mcp = FastMCP("blender-ai-mcp", dependencies=["pydantic", "fastmcp"])

# Global RPC Client
rpc = RpcClient()

@mcp.tool()
def list_objects() -> str:
    """List all objects in the current Blender scene with their types."""
    response = rpc.send_request("scene.list_objects")
    if response.status == "error":
        return f"Error: {response.error}"
    return str(response.result)

@mcp.tool()
def delete_object(name: str) -> str:
    """Delete an object from the scene by name."""
    response = rpc.send_request("scene.delete_object", {"name": name})
    if response.status == "error":
        return f"Error: {response.error}"
    return f"Successfully deleted object: {name}"

@mcp.tool()
def clean_scene() -> str:
    """Delete ALL objects from the scene (Mesh, Curve, Surface, Meta, Font, Hair, PointCloud, Volume). Keeps Lights and Cameras by default."""
    response = rpc.send_request("scene.clean_scene")
    if response.status == "error":
        return f"Error: {response.error}"
    return "Scene cleaned."

if __name__ == "__main__":
    mcp.run()
