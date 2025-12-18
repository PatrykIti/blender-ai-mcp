"""
Router Adapters Layer.

Contains MCP integration and external interfaces.
"""

from server.router.adapters.mcp_integration import (
    MCPRouterIntegration,
    RouterMiddleware,
    create_router_integration,
    with_router,
)

__all__ = [
    "MCPRouterIntegration",
    "RouterMiddleware",
    "create_router_integration",
    "with_router",
]
