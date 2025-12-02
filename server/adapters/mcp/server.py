import logging
from server.adapters.mcp.instance import mcp
# Import areas to register tools
import server.adapters.mcp.areas
from server.infrastructure.di import is_router_enabled, get_router

logger = logging.getLogger(__name__)


def run():
    """Starts the MCP server."""
    if is_router_enabled():
        logger.info("Router Supervisor ENABLED - initializing...")
        router = get_router()
        if router:
            logger.info("Router Supervisor initialized - ready for LLM tool call processing")
            logger.info(f"Router config: {router.get_config()}")
        else:
            logger.warning("Router enabled but failed to initialize")
    else:
        logger.info("Router Supervisor DISABLED - direct tool execution mode")

    mcp.run()
