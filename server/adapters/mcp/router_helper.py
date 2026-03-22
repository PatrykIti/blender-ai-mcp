"""
Router Helper for MCP Tools.

Provides utilities for routing tool calls through SupervisorRouter.
"""

from typing import Dict, Any, List, Optional, Callable
import logging

from server.adapters.mcp.contracts.correction_audit import (
    CorrectionAuditEventContract,
    CorrectionExecutionContract,
    CorrectionIntentContract,
    CorrectionVerificationContract,
)
from server.adapters.mcp.execution_context import MCPExecutionContext
from server.adapters.mcp.execution_report import MCPExecutionReport, ExecutionStep
from server.infrastructure.di import is_router_enabled, get_router
from server.adapters.mcp.dispatcher import get_dispatcher

logger = logging.getLogger(__name__)


def _build_correction_audit_events(
    *,
    original_tool_name: str,
    original_params: Dict[str, Any],
    corrected_tools: List[Dict[str, Any]],
    steps: List[ExecutionStep],
    policy_context: dict[str, Any] | None = None,
) -> tuple[CorrectionAuditEventContract, ...]:
    """Build coarse audit events for router-applied sequence changes."""

    if not corrected_tools or not steps:
        return ()

    if len(corrected_tools) > 1:
        category = "workflow_expansion"
    else:
        corrected_tool = corrected_tools[0]["tool"]
        corrected_params = corrected_tools[0]["params"]
        if corrected_tool != original_tool_name:
            category = "tool_override"
        elif corrected_params != original_params:
            category = "parameter_rewrite"
        else:
            return ()

    events: list[CorrectionAuditEventContract] = []
    for index, (tool, step) in enumerate(zip(corrected_tools, steps), 1):
        events.append(
            CorrectionAuditEventContract(
                event_id=f"audit_{index}",
                decision=policy_context.get("decision") if policy_context else None,
                reason=policy_context.get("reason") if policy_context else None,
                confidence=policy_context,
                intent=CorrectionIntentContract(
                    original_tool_name=original_tool_name,
                    original_params=original_params,
                    corrected_tool_name=tool["tool"],
                    corrected_params=tool["params"],
                    category=category,
                ),
                execution=CorrectionExecutionContract(
                    tool_name=step.tool_name,
                    params=step.params,
                    result=step.result,
                    error=step.error,
                ),
                verification=CorrectionVerificationContract(),
            )
        )
    return tuple(events)


def route_tool_call_report(
    tool_name: str,
    params: Dict[str, Any],
    direct_executor: Callable[[], Any],
    prompt: Optional[str] = None,
) -> MCPExecutionReport:
    """Build a structured execution report for a tool call."""

    context = MCPExecutionContext(tool_name=tool_name, params=params, prompt=prompt)

    if not is_router_enabled():
        result = direct_executor()
        return MCPExecutionReport(
            context=context,
            router_enabled=False,
            router_applied=False,
            steps=(ExecutionStep(tool_name=tool_name, params=params, result=result),),
        )

    router = get_router()
    if router is None:
        result = direct_executor()
        return MCPExecutionReport(
            context=context,
            router_enabled=True,
            router_applied=False,
            steps=(ExecutionStep(tool_name=tool_name, params=params, result=result),),
        )

    try:
        corrected_tools = router.process_llm_tool_call(tool_name, params, prompt)

        if len(corrected_tools) == 1 and corrected_tools[0]["tool"] == tool_name:
            if corrected_tools[0]["params"] == params:
                result = direct_executor()
                return MCPExecutionReport(
                    context=context,
                    router_enabled=True,
                    router_applied=False,
                    steps=(ExecutionStep(tool_name=tool_name, params=params, result=result),),
                )

        dispatcher = get_dispatcher()
        steps: List[ExecutionStep] = []

        for index, tool in enumerate(corrected_tools):
            tool_to_execute = tool["tool"]
            tool_params = tool["params"]

            logger.debug(
                "Router executing step %s/%s: %s",
                index + 1,
                len(corrected_tools),
                tool_to_execute,
            )

            if tool_to_execute == tool_name and index == len(corrected_tools) - 1:
                result = (
                    direct_executor()
                    if tool_params == params
                    else dispatcher.execute(tool_to_execute, tool_params)
                )
            else:
                result = dispatcher.execute(tool_to_execute, tool_params)

            steps.append(
                ExecutionStep(tool_name=tool_to_execute, params=tool_params, result=result)
            )

        return MCPExecutionReport(
            context=context,
            router_enabled=True,
            router_applied=True,
            steps=tuple(steps),
            audit_events=_build_correction_audit_events(
                original_tool_name=tool_name,
                original_params=params,
                corrected_tools=corrected_tools,
                steps=steps,
            ),
        )

    except Exception as e:
        logger.error(f"Router processing failed for {tool_name}: {e}", exc_info=True)
        fallback_result = direct_executor()
        return MCPExecutionReport(
            context=context,
            router_enabled=True,
            router_applied=False,
            steps=(ExecutionStep(tool_name=tool_name, params=params, result=fallback_result),),
        )


def route_tool_call(
    tool_name: str,
    params: Dict[str, Any],
    direct_executor: Callable[[], Any],
    prompt: Optional[str] = None,
) -> Any:
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
    report = route_tool_call_report(
        tool_name=tool_name,
        params=params,
        direct_executor=direct_executor,
        prompt=prompt,
    )
    if report.error is None and len(report.steps) == 1:
        result = report.steps[0].result
        if not isinstance(result, str):
            return result
    return report.to_legacy_text()


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
    steps: List[ExecutionStep] = []

    for tool in tools:
        tool_name = tool.get("tool", "")
        params = tool.get("params", {})

        try:
            result = dispatcher.execute(tool_name, params)
            steps.append(ExecutionStep(tool_name=tool_name, params=params, result=result))
        except Exception as e:
            steps.append(
                ExecutionStep(
                    tool_name=tool_name,
                    params=params,
                    result=f"Error executing {tool_name}: {str(e)}",
                    error=str(e),
                )
            )

    report = MCPExecutionReport(
        context=MCPExecutionContext(tool_name="sequence", params={"tools": tools}),
        router_enabled=True,
        router_applied=True,
        steps=tuple(steps),
    )
    return report.to_legacy_text()


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
