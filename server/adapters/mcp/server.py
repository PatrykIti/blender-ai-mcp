import logging
import signal
import sys
from server.adapters.mcp.instance import mcp
# Import areas to register tools
import server.adapters.mcp.areas
from server.infrastructure.di import is_router_enabled, get_router

logger = logging.getLogger(__name__)

# Flag to track if shutdown was requested
_shutdown_requested = False


def _signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global _shutdown_requested
    if _shutdown_requested:
        # Force exit on second signal
        sys.exit(0)
    _shutdown_requested = True
    logger.info("Shutdown signal received, closing gracefully...")


def run():
    """Starts the MCP server."""
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

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

    try:
        mcp.run()
    except KeyboardInterrupt:
        # This is expected during client disconnect/reconnect cycles
        if not _shutdown_requested:
            logger.debug("Client disconnected (probe/healthcheck cycle)")
    except Exception as e:
        logger.error(f"MCP server error: {e}")
        raise
