from server.adapters.mcp.instance import mcp
# Import areas to register tools
import server.adapters.mcp.areas

def run():
    """Starts the MCP server."""
    mcp.run()
