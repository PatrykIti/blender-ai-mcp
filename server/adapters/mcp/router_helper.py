"""
Router Helper for MCP Tools.

Provides utilities for routing tool calls through SupervisorRouter.
"""

from typing import Dict, Any, List, Optional, Callable
import logging

from server.infrastructure.di import is_router_enabled, get_router
from server.adapters.mcp.dispatcher import get_dispatcher

logger = logging.getLogger(__name__)


def route_tool_call(
    tool_name: str,
    params: Dict[str, Any],
    direct_executor: Callable[[], str],
    prompt: Optional[str] = None,
) -> str:
    """Route a tool call through the Router Supervisor if enabled.

    This function should be called at the beginning of MCP tool functions
    to enable router processing.

    Args:
        tool_name: Name of the tool being called.
        params: Parameters passed to the tool.
        direct_executor: Lambda/function that executes the tool directly.
        prompt: Optional user prompt for better intent classification.

    Returns:
        Result string from tool execution (routed or direct).

    Example:
        @mcp.tool()
        def mesh_extrude_region(ctx: Context, depth: float = 1.0) -> str:
            return route_tool_call(
                tool_name="mesh_extrude_region",
                params={"depth": depth},
                direct_executor=lambda: get_mesh_handler().extrude_region(depth=depth),
            )
    """
    # If router is disabled, execute directly
    if not is_router_enabled():
        return direct_executor()

    router = get_router()
    if router is None:
        return direct_executor()

    try:
        # Process through router
        corrected_tools = router.process_llm_tool_call(tool_name, params, prompt)

        # If router returns single unchanged tool, execute directly
        if len(corrected_tools) == 1 and corrected_tools[0]["tool"] == tool_name:
            # Check if params are the same
            if corrected_tools[0]["params"] == params:
                return direct_executor()

        # Execute the corrected/expanded tool sequence
        dispatcher = get_dispatcher()
        results: List[str] = []

        for i, tool in enumerate(corrected_tools):
            tool_to_execute = tool["tool"]
            tool_params = tool["params"]

            logger.debug(f"Router executing step {i+1}/{len(corrected_tools)}: {tool_to_execute}")

            # If this is the original tool, use direct executor
            if tool_to_execute == tool_name and i == len(corrected_tools) - 1:
                # Use potentially modified params
                result = direct_executor() if tool_params == params else dispatcher.execute(tool_to_execute, tool_params)
            else:
                # Use dispatcher for other tools
                result = dispatcher.execute(tool_to_execute, tool_params)

            results.append(result)

        # Combine results
        if len(results) == 1:
            return results[0]

        # Format multi-step results
        combined_parts = []
        for i, (result, tool) in enumerate(zip(results, corrected_tools), 1):
            combined_parts.append(f"[Step {i}: {tool['tool']}] {result}")

        return "\n".join(combined_parts)

    except Exception as e:
        logger.error(f"Router processing failed for {tool_name}: {e}", exc_info=True)
        # Fallback to direct execution
        return direct_executor()


def execute_routed_sequence(tools: List[Dict[str, Any]]) -> str:
    """Execute a sequence of tools from router.

    Args:
        tools: List of tool dicts with 'tool' and 'params' keys.

    Returns:
        Combined result string.
    """
    if not tools:
        return "No operations performed."

    dispatcher = get_dispatcher()
    results: List[str] = []

    for tool in tools:
        tool_name = tool.get("tool", "")
        params = tool.get("params", {})

        try:
            result = dispatcher.execute(tool_name, params)
            results.append(result)
        except Exception as e:
            results.append(f"Error executing {tool_name}: {str(e)}")

    if len(results) == 1:
        return results[0]

    combined_parts = []
    for i, (result, tool) in enumerate(zip(results, tools), 1):
        combined_parts.append(f"[Step {i}: {tool['tool']}] {result}")

    return "\n".join(combined_parts)


def get_router_status() -> Dict[str, Any]:
    """Get current router status.

    Returns:
        Dictionary with router status info.
    """
    enabled = is_router_enabled()

    if not enabled:
        return {
            "enabled": False,
            "message": "Router Supervisor is disabled. Set ROUTER_ENABLED=true to enable.",
        }

    router = get_router()
    if router is None:
        return {
            "enabled": True,
            "initialized": False,
            "message": "Router enabled but not initialized.",
        }

    return {
        "enabled": True,
        "initialized": True,
        "ready": router.is_ready(),
        "component_status": router.get_component_status(),
        "stats": router.get_stats(),
        "config": str(router.get_config()),
    }
