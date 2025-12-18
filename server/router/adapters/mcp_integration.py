"""
MCP Integration Adapter.

Hooks the Router Supervisor into the MCP server tool execution pipeline.
"""

from typing import Dict, Any, List, Callable, Awaitable, Optional, Set
from functools import wraps
import asyncio
import logging

from server.router.application.router import SupervisorRouter
from server.router.infrastructure.config import RouterConfig


logger = logging.getLogger(__name__)


class MCPRouterIntegration:
    """Integrates Router Supervisor with MCP server.

    Wraps tool execution to route through supervisor pipeline.
    Supports both sync and async execution modes.

    Attributes:
        router: SupervisorRouter instance.
        config: Router configuration.
        enabled: Whether routing is enabled.
        bypass_tools: Tools that bypass the router.
    """

    def __init__(
        self,
        router: Optional[SupervisorRouter] = None,
        config: Optional[RouterConfig] = None,
        enabled: bool = True,
    ):
        """Initialize MCP integration.

        Args:
            router: SupervisorRouter instance.
            config: Router configuration.
            enabled: Whether routing is enabled by default.
        """
        self.config = config or RouterConfig()
        self.router = router or SupervisorRouter(config=self.config)
        self.enabled = enabled
        self._original_executor: Optional[Callable] = None
        self._bypass_tools: Set[str] = set()
        self._execution_count = 0
        self._error_count = 0

    def set_rpc_client(self, rpc_client: Any) -> None:
        """Set the RPC client for Blender communication.

        Args:
            rpc_client: RPC client instance.
        """
        self.router.set_rpc_client(rpc_client)

    def enable(self) -> None:
        """Enable router integration."""
        self.enabled = True
        logger.info("Router integration enabled")

    def disable(self) -> None:
        """Disable router integration."""
        self.enabled = False
        logger.info("Router integration disabled")

    def add_bypass_tool(self, tool_name: str) -> None:
        """Add a tool to bypass the router.

        Args:
            tool_name: Tool name to bypass.
        """
        self._bypass_tools.add(tool_name)

    def remove_bypass_tool(self, tool_name: str) -> None:
        """Remove a tool from bypass list.

        Args:
            tool_name: Tool name to remove from bypass.
        """
        self._bypass_tools.discard(tool_name)

    def should_bypass(self, tool_name: str) -> bool:
        """Check if a tool should bypass the router.

        Args:
            tool_name: Tool name to check.

        Returns:
            True if tool should bypass.
        """
        return tool_name in self._bypass_tools

    def wrap_tool_executor(
        self,
        executor: Callable[[str, Dict[str, Any]], Awaitable[str]],
    ) -> Callable[[str, Dict[str, Any]], Awaitable[str]]:
        """Wrap a tool executor with router processing.

        Args:
            executor: Original async tool executor function.

        Returns:
            Wrapped executor that routes through supervisor.
        """
        self._original_executor = executor

        @wraps(executor)
        async def wrapped_executor(tool_name: str, params: Dict[str, Any]) -> str:
            self._execution_count += 1

            # Check if disabled or bypassed
            if not self.enabled or self.should_bypass(tool_name):
                return await executor(tool_name, params)

            try:
                # Route through supervisor
                corrected_tools = self.router.process_llm_tool_call(tool_name, params)

                # Execute each tool in sequence
                results: List[str] = []
                for tool in corrected_tools:
                    try:
                        result = await executor(tool["tool"], tool["params"])
                        results.append(result)
                    except Exception as e:
                        self._error_count += 1
                        logger.error(f"Tool execution failed: {tool['tool']}: {e}")
                        results.append(f"Error executing {tool['tool']}: {str(e)}")

                # Combine results
                return self._combine_results(results, corrected_tools)

            except Exception as e:
                self._error_count += 1
                logger.error(f"Router processing failed: {e}")
                # Fallback to original execution
                return await executor(tool_name, params)

        return wrapped_executor

    def wrap_sync_executor(
        self,
        executor: Callable[[str, Dict[str, Any]], str],
    ) -> Callable[[str, Dict[str, Any]], str]:
        """Wrap a synchronous tool executor with router processing.

        Args:
            executor: Original sync tool executor function.

        Returns:
            Wrapped executor that routes through supervisor.
        """
        @wraps(executor)
        def wrapped_executor(tool_name: str, params: Dict[str, Any]) -> str:
            self._execution_count += 1

            # Check if disabled or bypassed
            if not self.enabled or self.should_bypass(tool_name):
                return executor(tool_name, params)

            try:
                # Route through supervisor
                corrected_tools = self.router.process_llm_tool_call(tool_name, params)

                # Execute each tool in sequence
                results: List[str] = []
                for tool in corrected_tools:
                    try:
                        result = executor(tool["tool"], tool["params"])
                        results.append(result)
                    except Exception as e:
                        self._error_count += 1
                        logger.error(f"Tool execution failed: {tool['tool']}: {e}")
                        results.append(f"Error executing {tool['tool']}: {str(e)}")

                # Combine results
                return self._combine_results(results, corrected_tools)

            except Exception as e:
                self._error_count += 1
                logger.error(f"Router processing failed: {e}")
                # Fallback to original execution
                return executor(tool_name, params)

        return wrapped_executor

    def _combine_results(
        self,
        results: List[str],
        tools: List[Dict[str, Any]],
    ) -> str:
        """Combine multiple tool results into single response.

        Args:
            results: List of result strings.
            tools: List of executed tools.

        Returns:
            Combined result string.
        """
        if len(results) == 0:
            return "No operations performed."

        if len(results) == 1:
            return results[0]

        # Combine with tool context
        combined_parts = []
        for i, (result, tool) in enumerate(zip(results, tools), 1):
            tool_name = tool.get("tool", "unknown")
            combined_parts.append(f"[Step {i}: {tool_name}] {result}")

        return "\n".join(combined_parts)

    def get_stats(self) -> Dict[str, Any]:
        """Get integration statistics.

        Returns:
            Dictionary with stats.
        """
        router_stats = self.router.get_stats()
        return {
            "enabled": self.enabled,
            "execution_count": self._execution_count,
            "error_count": self._error_count,
            "bypass_tools": list(self._bypass_tools),
            "router_stats": router_stats,
        }

    def reset_stats(self) -> None:
        """Reset integration statistics."""
        self._execution_count = 0
        self._error_count = 0
        self.router.reset_stats()


class RouterMiddleware:
    """Middleware-style router integration for MCP servers.

    Provides a more flexible integration pattern that can be
    inserted into various MCP server implementations.
    """

    def __init__(
        self,
        integration: Optional[MCPRouterIntegration] = None,
        config: Optional[RouterConfig] = None,
    ):
        """Initialize middleware.

        Args:
            integration: MCPRouterIntegration instance.
            config: Router configuration.
        """
        self.integration = integration or MCPRouterIntegration(config=config)

    def __call__(
        self,
        next_handler: Callable[[str, Dict[str, Any]], Awaitable[str]],
    ) -> Callable[[str, Dict[str, Any]], Awaitable[str]]:
        """Create middleware handler.

        Args:
            next_handler: Next handler in chain.

        Returns:
            Wrapped handler.
        """
        return self.integration.wrap_tool_executor(next_handler)


def create_router_integration(
    config: Optional[RouterConfig] = None,
    rpc_client: Optional[Any] = None,
    enabled: bool = True,
    bypass_tools: Optional[List[str]] = None,
) -> MCPRouterIntegration:
    """Factory function to create configured router integration.

    Args:
        config: Router configuration.
        rpc_client: RPC client for Blender.
        enabled: Whether routing is enabled.
        bypass_tools: List of tools to bypass.

    Returns:
        Configured MCPRouterIntegration instance.
    """
    config = config or RouterConfig()
    router = SupervisorRouter(config=config, rpc_client=rpc_client)
    integration = MCPRouterIntegration(
        router=router,
        config=config,
        enabled=enabled,
    )

    if bypass_tools:
        for tool in bypass_tools:
            integration.add_bypass_tool(tool)

    return integration


# Decorator for easy tool wrapping
def with_router(
    integration: MCPRouterIntegration,
) -> Callable:
    """Decorator to wrap individual tool functions with router.

    Args:
        integration: MCPRouterIntegration instance.

    Returns:
        Decorator function.

    Usage:
        @with_router(integration)
        async def my_tool(params):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> str:
            # Extract tool name from function
            tool_name = func.__name__

            # Get params from args/kwargs
            if args:
                params = args[0] if isinstance(args[0], dict) else kwargs
            else:
                params = kwargs

            # Route through integration
            if integration.enabled and not integration.should_bypass(tool_name):
                corrected_tools = integration.router.process_llm_tool_call(
                    tool_name, params
                )

                # If unchanged, call original
                if len(corrected_tools) == 1 and corrected_tools[0]["tool"] == tool_name:
                    return await func(*args, **kwargs)

                # Execute corrected tools
                results = []
                for tool in corrected_tools:
                    if tool["tool"] == tool_name:
                        result = await func(tool["params"])
                    else:
                        # Would need executor for other tools
                        results.append(f"Skipped {tool['tool']}: no executor")
                        continue
                    results.append(result)

                return integration._combine_results(results, corrected_tools)

            return await func(*args, **kwargs)

        return wrapper
    return decorator
