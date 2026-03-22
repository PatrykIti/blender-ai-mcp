# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""
MCP server entrypoint.

Author: Patryk Ciechański (PatrykIti)
"""

import logging
import signal
import sys
from server.adapters.mcp.factory import build_server
from server.infrastructure.di import is_router_enabled, get_router
from server.infrastructure.config import get_config

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


def run(surface_profile: str | None = None):
    """Starts the MCP server."""
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    config = get_config()
    selected_surface = surface_profile or config.MCP_SURFACE_PROFILE
    server = build_server(surface_profile=selected_surface)

    # Log router status (lazy loading via DI on first tool use)
    if is_router_enabled():
        logger.info("Router Supervisor ENABLED - lazy loading via DI")
    else:
        logger.info("Router Supervisor DISABLED - direct tool execution mode")
    logger.info("MCP surface profile: %s", selected_surface)

    try:
        server.run()
    except KeyboardInterrupt:
        # This is expected during client disconnect/reconnect cycles
        if not _shutdown_requested:
            logger.debug("Client disconnected (probe/healthcheck cycle)")
    except Exception as e:
        logger.error(f"MCP server error: {e}")
        raise
