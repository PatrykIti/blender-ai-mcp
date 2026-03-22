"""
Router Helper for MCP Tools.

Provides utilities for routing tool calls through SupervisorRouter.
"""

import logging
from typing import Any, Callable, Dict, List, Optional, cast

from server.adapters.mcp.contracts.correction_audit import (
    CorrectionAuditEventContract,
    CorrectionExecutionContract,
    CorrectionIntentContract,
    CorrectionVerificationContract,
)
from server.adapters.mcp.dispatcher import get_dispatcher
from server.adapters.mcp.execution_context import MCPExecutionContext
from server.adapters.mcp.execution_report import ExecutionStep, MCPExecutionReport
from server.adapters.mcp.session_capabilities import record_router_execution_outcome
from server.adapters.mcp.session_state import set_session_value
from server.infrastructure.config import get_config
from server.infrastructure.di import get_postcondition_registry, get_router, get_scene_handler, is_router_enabled
from server.router.domain.entities.correction_policy import CorrectionCategory
from server.router.infrastructure.logger import get_router_logger

logger = logging.getLogger(__name__)

SESSION_LAST_ROUTER_DISPOSITION_KEY = "last_router_disposition"
SESSION_LAST_ROUTER_ERROR_KEY = "last_router_error"


def _get_active_surface_profile() -> str:
    """Return the active surface profile for the current tool call."""

    try:
        from fastmcp.server.context import _current_context  # type: ignore

        current_ctx = _current_context.get(None)
        if current_ctx is not None:
            server = current_ctx.fastmcp
            return getattr(server, "_bam_surface_profile", get_config().MCP_SURFACE_PROFILE)
    except Exception:
        pass

    return get_config().MCP_SURFACE_PROFILE


def _should_fail_closed_on_router_error(surface_profile: str) -> bool:
    """Guided/product surfaces fail closed; explicit compatibility stays fail-open."""

    return surface_profile != "legacy-flat"


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

    events: list[CorrectionAuditEventContract] = []
    for index, (tool, step) in enumerate(zip(corrected_tools, steps), 1):
        corrected_tool_name = tool["tool"]
        corrected_params = tool["params"]

        if corrected_tool_name == "system_set_mode" and original_tool_name != "system_set_mode":
            category = "precondition_mode"
        elif corrected_tool_name in {"mesh_select", "mesh_select_targeted"} and original_tool_name not in {
            "mesh_select",
            "mesh_select_targeted",
        }:
            category = "precondition_selection"
        elif corrected_tool_name == "scene_set_active_object" and original_tool_name != "scene_set_active_object":
            category = "precondition_active_object"
        elif len(corrected_tools) > 1 and corrected_tool_name != original_tool_name:
            category = "workflow_expansion"
        elif corrected_tool_name != original_tool_name:
            category = "tool_override"
        elif corrected_params != original_params:
            category = "parameter_rewrite"
        else:
            continue

        events.append(
            CorrectionAuditEventContract(
                event_id=f"audit_{index}",
                decision=policy_context.get("decision") if policy_context else None,
                reason=policy_context.get("reason") if policy_context else None,
                confidence=policy_context,
                intent=CorrectionIntentContract(
                    original_tool_name=original_tool_name,
                    original_params=original_params,
                    corrected_tool_name=corrected_tool_name,
                    corrected_params=corrected_params,
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


def _extract_audit_ids(
    audit_events: tuple[CorrectionAuditEventContract, ...],
) -> tuple[str, ...]:
    """Return stable audit identifiers for exposure in reports and logs."""

    return tuple(event.event_id for event in audit_events)


def _log_audit_exposure(report: MCPExecutionReport) -> None:
    """Emit one structured log line for correction audit visibility."""

    if not report.audit_ids and report.router_disposition in {"bypassed", "direct"}:
        return

    get_router_logger().log_execution_audit(
        tool_name=report.context.tool_name,
        disposition=report.router_disposition,
        verification_status=report.verification_status,
        audit_ids=list(report.audit_ids),
    )


def _record_router_execution_report(report: MCPExecutionReport) -> None:
    """Persist the last router execution outcome in session state when available."""

    try:
        from fastmcp.server.context import _current_context  # type: ignore

        current_ctx = _current_context.get(None)
    except Exception:
        current_ctx = None

    if current_ctx is None:
        return

    try:
        record_router_execution_outcome(
            current_ctx,
            router_disposition=report.router_disposition,
            error=report.error,
        )
    except Exception:
        try:
            set_session_value(current_ctx, SESSION_LAST_ROUTER_DISPOSITION_KEY, report.router_disposition)
            set_session_value(current_ctx, SESSION_LAST_ROUTER_ERROR_KEY, report.error)
        except Exception:
            return


def _apply_postcondition_verification(
    audit_events: tuple[CorrectionAuditEventContract, ...],
) -> tuple[tuple[CorrectionAuditEventContract, ...], str]:
    """Evaluate inspection-based verification for registered high-risk correction events."""

    if not audit_events:
        return audit_events, "not_requested"

    registry = get_postcondition_registry()
    scene_handler = get_scene_handler()

    updated_events: list[CorrectionAuditEventContract] = []
    statuses: list[str] = []

    for event in audit_events:
        try:
            category = CorrectionCategory(event.intent.category)
        except ValueError:
            updated_events.append(event)
            continue

        requirement = registry.get(category)
        if requirement is None:
            updated_events.append(event)
            continue

        status = "inconclusive"
        details: dict[str, Any] | None = None

        try:
            if requirement.verification_key == "verify_mode":
                mode_payload = scene_handler.get_mode()
                expected_mode = event.execution.params.get("mode") or event.intent.corrected_params.get("mode")
                actual_mode = mode_payload.get("mode")
                status = "passed" if expected_mode == actual_mode else "failed"
                details = {"expected_mode": expected_mode, "actual_mode": actual_mode}
            elif requirement.verification_key == "verify_selection":
                selection_payload = scene_handler.list_selection()
                selection_count = selection_payload.get("selection_count", 0)
                status = "passed" if selection_count > 0 else "failed"
                details = {"selection_count": selection_count}
            elif requirement.verification_key == "verify_active_object":
                mode_payload = scene_handler.get_mode()
                expected_object = event.execution.params.get("name") or event.intent.corrected_params.get("name")
                actual_object = mode_payload.get("active_object")
                status = "passed" if expected_object == actual_object else "failed"
                details = {"expected_object": expected_object, "actual_object": actual_object}
        except Exception as exc:
            status = "inconclusive"
            details = {"error": str(exc), "verification_key": requirement.verification_key}

        statuses.append(status)
        updated_events.append(
            event.model_copy(
                update={
                    "verification": CorrectionVerificationContract(
                        status=status,
                        details=details,
                    )
                }
            )
        )

    if not statuses:
        return tuple(updated_events), "not_requested"
    if any(status == "failed" for status in statuses):
        overall = "failed"
    elif any(status == "inconclusive" for status in statuses):
        overall = "inconclusive"
    elif all(status == "passed" for status in statuses):
        overall = "passed"
    else:
        overall = "pending"
    return tuple(updated_events), overall


def route_tool_call_report(
    tool_name: str,
    params: Dict[str, Any],
    direct_executor: Callable[[], Any],
    prompt: Optional[str] = None,
) -> MCPExecutionReport:
    """Build a structured execution report for a tool call."""

    context = MCPExecutionContext(tool_name=tool_name, params=params, prompt=prompt)
    surface_profile = _get_active_surface_profile()
    context.surface_profile = surface_profile

    if not is_router_enabled():
        result = direct_executor()
        report = MCPExecutionReport(
            context=context,
            router_enabled=False,
            router_applied=False,
            router_disposition="bypassed",
            steps=(ExecutionStep(tool_name=tool_name, params=params, result=result),),
            audit_ids=(),
        )
        _record_router_execution_report(report)
        _log_audit_exposure(report)
        return report

    router = get_router()
    if router is None:
        if _should_fail_closed_on_router_error(surface_profile):
            report = MCPExecutionReport(
                context=context,
                router_enabled=True,
                router_applied=False,
                router_disposition="failed_closed_error",
                error="Router is enabled but not initialized for this guided surface.",
                audit_ids=(),
            )
            _record_router_execution_report(report)
            _log_audit_exposure(report)
            return report

        result = direct_executor()
        report = MCPExecutionReport(
            context=context,
            router_enabled=True,
            router_applied=False,
            router_disposition="bypassed",
            steps=(ExecutionStep(tool_name=tool_name, params=params, result=result),),
            audit_ids=(),
        )
        _record_router_execution_report(report)
        _log_audit_exposure(report)
        return report

    try:
        corrected_tools = router.process_llm_tool_call(tool_name, params, prompt)

        if len(corrected_tools) == 1 and corrected_tools[0]["tool"] == tool_name:
            if corrected_tools[0]["params"] == params:
                result = direct_executor()
                report = MCPExecutionReport(
                    context=context,
                    router_enabled=True,
                    router_applied=False,
                    router_disposition="direct",
                    steps=(ExecutionStep(tool_name=tool_name, params=params, result=result),),
                    audit_ids=(),
                )
                _record_router_execution_report(report)
                _log_audit_exposure(report)
                return report

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
                    direct_executor() if tool_params == params else dispatcher.execute(tool_to_execute, tool_params)
                )
            else:
                result = dispatcher.execute(tool_to_execute, tool_params)

            steps.append(ExecutionStep(tool_name=tool_to_execute, params=tool_params, result=result))

        audit_events = _build_correction_audit_events(
            original_tool_name=tool_name,
            original_params=params,
            corrected_tools=corrected_tools,
            steps=steps,
        )
        audit_events, verification_status = _apply_postcondition_verification(audit_events)

        report = MCPExecutionReport(
            context=context,
            router_enabled=True,
            router_applied=True,
            router_disposition="corrected",
            steps=tuple(steps),
            audit_events=audit_events,
            audit_ids=_extract_audit_ids(audit_events),
            verification_status=cast(Any, verification_status),
        )
        _record_router_execution_report(report)
        _log_audit_exposure(report)
        return report

    except Exception as e:
        logger.error(f"Router processing failed for {tool_name}: {e}", exc_info=True)
        if _should_fail_closed_on_router_error(surface_profile):
            report = MCPExecutionReport(
                context=context,
                router_enabled=True,
                router_applied=False,
                router_disposition="failed_closed_error",
                error=f"Router processing failed for {tool_name}: {e}",
                audit_ids=(),
            )
            _record_router_execution_report(report)
            _log_audit_exposure(report)
            return report

        fallback_result = direct_executor()
        report = MCPExecutionReport(
            context=context,
            router_enabled=True,
            router_applied=False,
            router_disposition="failed_open_fallback",
            steps=(ExecutionStep(tool_name=tool_name, params=params, result=fallback_result),),
            audit_ids=(),
        )
        _record_router_execution_report(report)
        _log_audit_exposure(report)
        return report


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
        router_disposition="corrected",
        steps=tuple(steps),
        audit_ids=(),
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
        "assistant_diagnostics": router.get_assistant_diagnostics(),
    }
