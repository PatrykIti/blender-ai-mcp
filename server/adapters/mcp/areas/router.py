"""
Router MCP Tools.

Tools for goal-first session bootstrap and router-aware workflow/status interaction.
On production-oriented surfaces, these tools anchor the active goal/session
context instead of acting as optional decoration around a flat catalog.

Follows Clean Architecture pattern:
- MCP adapter layer calls Application layer (RouterToolHandler)
- Handler implements Domain interface (IRouterTool)

TASK-046: Extended with semantic matching tools.
TASK-055-FIX: Unified parameter resolution through single router_set_goal tool.
"""

from typing import Any, Dict, List, Optional, cast

from fastmcp import Context

from server.adapters.mcp.context_utils import ctx_info
from server.adapters.mcp.contracts.router import (
    RouterGoalResponseContract,
    RouterStatusContract,
)
from server.adapters.mcp.elicitation_contracts import (
    build_clarification_plan,
    build_fallback_payload,
)
from server.adapters.mcp.guided_mode import build_visibility_diagnostics
from server.adapters.mcp.router_helper import get_router_status
from server.adapters.mcp.sampling.assistant_runner import run_repair_suggestion_assistant
from server.adapters.mcp.sampling.result_types import to_repair_assistant_contract
from server.adapters.mcp.session_capabilities import (
    apply_visibility_for_session_state,
    clear_session_goal_state_async,
    get_session_capability_state_async,
    merge_resolved_params_with_session_answers_async,
    update_session_from_router_goal_async,
)
from server.adapters.mcp.tasks.job_registry import get_background_job_registry
from server.adapters.mcp.visibility.tags import get_capability_tags
from server.infrastructure.config import get_config
from server.infrastructure.di import get_router_handler
from server.infrastructure.telemetry import get_telemetry_state

ROUTER_PUBLIC_TOOL_NAMES = (
    "router_set_goal",
    "router_get_status",
    "router_clear_goal",
    "router_find_similar_workflows",
    "router_get_inherited_proportions",
    "router_feedback",
)


def _register_existing_tool(target: Any, tool_name: str) -> Any:
    """Register an existing router tool on a FastMCP-compatible target."""

    tool = globals()[tool_name]
    fn = getattr(tool, "fn", tool)
    return target.tool(fn, name=tool_name, tags=set(get_capability_tags("router")))


def register_router_tools(target: Any) -> Dict[str, Any]:
    """Register public router tools on a FastMCP server or LocalProvider."""

    return {tool_name: _register_existing_tool(target, tool_name) for tool_name in ROUTER_PUBLIC_TOOL_NAMES}


def _get_runtime_contract_line(ctx: Context) -> str | None:
    """Best-effort current contract-line lookup from the running server."""

    try:
        return getattr(ctx.fastmcp, "_bam_contract_line", None)
    except Exception:
        return None


def _build_background_job_diagnostics() -> tuple[int, dict[str, int], list[dict[str, Any]]]:
    """Return background job diagnostics from the shared task registry."""

    jobs = [job.to_dict() for job in get_background_job_registry().list()]
    counts_by_status: dict[str, int] = {}
    for job in jobs:
        status = str(job.get("status") or "unknown")
        counts_by_status[status] = counts_by_status.get(status, 0) + 1
    return len(jobs), counts_by_status, jobs


def _build_telemetry_diagnostics() -> dict[str, Any]:
    """Return a diagnostics-friendly telemetry snapshot."""

    state = get_telemetry_state()
    return {
        "enabled": state.enabled,
        "service_name": state.service_name,
        "exporter": state.exporter,
        "provider_configured": state.provider is not None,
        "memory_exporter_enabled": state.memory_exporter is not None,
    }


def _build_task_runtime_diagnostics(ctx: Context) -> dict[str, Any] | None:
    """Return the active task-runtime diagnostics for the current server surface."""

    try:
        report = getattr(ctx.fastmcp, "_bam_task_runtime_report", None)
    except Exception:
        report = None

    if report is None:
        return None
    try:
        return report.to_dict()
    except Exception:
        return None


def _build_timeout_policy_diagnostics(ctx: Context) -> dict[str, Any] | None:
    """Return timeout policy diagnostics attached by the factory."""

    try:
        policy = getattr(ctx.fastmcp, "_bam_timeout_policy", None)
    except Exception:
        policy = None

    if policy is None:
        return None
    try:
        return policy.to_dict()
    except Exception:
        return None


def _get_list_page_size(ctx: Context) -> int | None:
    """Return the current server list page size when available."""

    try:
        return getattr(ctx.fastmcp, "list_page_size", None)
    except Exception:
        return None


def _should_attach_repair_suggestion(payload: Dict[str, Any]) -> bool:
    """Return True when router diagnostics justify bounded repair guidance."""

    status = payload.get("status")
    if status in {"no_match", "error"}:
        return True
    if payload.get("last_router_error"):
        return True
    return payload.get("last_router_disposition") in {
        "failed_closed_error",
        "failed_open_fallback",
    }


def _build_repair_diagnostics(
    payload: Dict[str, Any],
    *,
    source: str,
) -> Dict[str, Any]:
    """Build a bounded diagnostic payload for the repair assistant."""

    diagnostics = {
        "source": source,
        "status": payload.get("status"),
        "workflow": payload.get("workflow"),
        "message": payload.get("message"),
        "error": payload.get("error"),
        "unresolved": payload.get("unresolved"),
        "policy_context": payload.get("policy_context"),
        "last_router_status": payload.get("last_router_status"),
        "last_router_disposition": payload.get("last_router_disposition"),
        "last_router_error": payload.get("last_router_error"),
        "router_failure_policy": payload.get("router_failure_policy"),
        "assistant_diagnostics": payload.get("assistant_diagnostics"),
    }
    return {key: value for key, value in diagnostics.items() if value is not None}


def _contains_model_facing_workflow_confirmation(result: Dict[str, Any]) -> bool:
    """Return True when clarification should stay model-facing instead of eliciting the human."""

    unresolved = result.get("unresolved") or []
    for item in unresolved:
        if isinstance(item, dict) and item.get("param") == "workflow_confirmation":
            return True
    return False


async def _maybe_elicit_router_answers(
    ctx: Context,
    goal: str,
    result: Dict[str, Any],
) -> Dict[str, Any]:
    """Build the typed clarification payload for missing router parameters.

    On llm-guided, workflow clarification is model-facing by default.
    Human/native elicitation is reserved for later/fallback policy, not the
    first response path.
    """

    if get_config().MCP_SURFACE_PROFILE != "llm-guided":
        return result

    if result.get("status") != "needs_input":
        return result

    session = await get_session_capability_state_async(ctx)
    plan = build_clarification_plan(
        goal=goal,
        workflow_name=result.get("workflow") or "unknown_workflow",
        unresolved_fields=result.get("unresolved", []),
    )
    if plan.is_empty:
        return result

    try:
        request_id = getattr(ctx, "request_id", None)
    except Exception:
        request_id = None
    else:
        if callable(request_id):
            try:
                request_id = request_id()
            except Exception:
                request_id = None
        elif request_id is not None and not isinstance(request_id, str):
            try:
                request_id = str(request_id)
            except Exception:
                request_id = None

    fallback_payload = build_fallback_payload(
        plan,
        request_id=request_id,
        question_set_id=session.pending_question_set_id,
    )
    result["clarification"] = fallback_payload.model_dump()
    return result


async def router_set_goal(
    ctx: Context,
    goal: str,
    resolved_params: Optional[Dict[str, Any]] = None,
) -> RouterGoalResponseContract:
    """
    [SYSTEM][CRITICAL] Set the active build goal for the current router session.

    On goal-first guided surfaces, call this before build operations so the
    router can select a workflow, resolve parameters, and shape the session.

    Normal interaction flow:
    1. First call sets the goal, matches a workflow, and resolves what it can.
    2. If unresolved params remain, the response returns what still needs input.
    3. Follow-up calls pass `resolved_params` so the router can continue.

    The Router uses a three-tier resolution system:
    1. YAML modifiers (highest priority) - explicit mappings in workflow definition
    2. Learned mappings (LaBSE) - semantic matches from previous interactions
    3. Interactive (you provide) - when no match found

    Learned mappings are stored automatically for future semantic reuse.

    Args:
        goal: What you're creating. Be specific with natural language modifiers!
              Examples: "smartphone", "picnic table with straight legs",
                       "stół z prostymi nogami", "medieval tower"
        resolved_params: Optional dict of parameter values when answering Router questions.
                        Use this on second call after receiving "needs_input" status.
                        Example: {"leg_angle_left": 0, "leg_angle_right": 0}

    Returns:
        JSON with:
        - status: "ready" | "needs_input" | "no_match" | "disabled" | "error"
        - workflow: matched workflow name
        - resolved: dict of resolved parameter values with sources
        - unresolved: list of parameters needing your input (when status="needs_input")
        - message: human-readable next steps

    Example - Simple case (all resolved):
        router_set_goal("picnic table with straight legs")
        -> {"status": "ready", "workflow": "picnic_table", "resolved": {...}}

    Example - Interactive case:
        # Step 1: Set goal with unknown modifier
        router_set_goal("stół z nogami pod kątem")
        -> {"status": "needs_input", "unresolved": [{"param": "leg_angle_left", ...}]}

        # Step 2: Provide values
        router_set_goal("stół z nogami pod kątem", resolved_params={"leg_angle_left": 15})
        -> {"status": "ready", "resolved": {"leg_angle_left": 15, ...}}

        # Future: Similar prompts auto-resolve via LaBSE semantic matching
        router_set_goal("stół z pochylonymi nogami")
        -> {"status": "ready", ...}  # Learned from previous interaction
    """
    handler = get_router_handler()
    merged_resolved_params = await merge_resolved_params_with_session_answers_async(ctx, resolved_params)
    result = handler.set_goal(goal, merged_resolved_params)

    if resolved_params is None and result.get("status") == "needs_input":
        result = await _maybe_elicit_router_answers(ctx, goal, result)
        if result.get("elicitation_action") == "accept":
            merged_answers = dict(merged_resolved_params or {})
            merged_answers.update(result.get("elicitation_answers") or {})
            result = handler.set_goal(
                goal,
                resolved_params=merged_answers,
            )

    if result.get("status") == "needs_input" and "clarification" not in result:
        plan = build_clarification_plan(
            goal=goal,
            workflow_name=result.get("workflow") or "unknown_workflow",
            unresolved_fields=result.get("unresolved", []),
        )
        if not plan.is_empty:
            try:
                request_id = getattr(ctx, "request_id", None)
            except Exception:
                request_id = None
            session = await get_session_capability_state_async(ctx)
            result["clarification"] = build_fallback_payload(
                plan,
                request_id=request_id if isinstance(request_id, str) else None,
                question_set_id=session.pending_question_set_id,
            ).model_dump()

    state = await update_session_from_router_goal_async(
        ctx,
        goal,
        result,
        provided_answers=merged_resolved_params,
        surface_profile=get_config().MCP_SURFACE_PROFILE,
        contract_version=_get_runtime_contract_line(ctx),
    )
    await apply_visibility_for_session_state(ctx, state)

    # Log to context
    status = result.get("status", "unknown")
    workflow = result.get("workflow")
    if status == "ready":
        ctx_info(ctx, f"[ROUTER] Goal set: {goal} -> workflow '{workflow}' ready")
    elif status == "needs_input":
        unresolved_count = len(result.get("unresolved", []))
        ctx_info(ctx, f"[ROUTER] Goal set: {goal} -> {unresolved_count} params need input")
    else:
        ctx_info(ctx, f"[ROUTER] Goal set: {goal} -> status: {status}")

    if _should_attach_repair_suggestion(result):
        repair_outcome = await run_repair_suggestion_assistant(
            ctx,
            diagnostics=_build_repair_diagnostics(result, source="router_set_goal"),
        )
        result["repair_suggestion"] = to_repair_assistant_contract(repair_outcome).model_dump()

    return RouterGoalResponseContract.model_validate(result)


async def router_get_status(ctx: Context) -> RouterStatusContract:
    """
    [SYSTEM][SAFE] Get the current router session and diagnostics state.

    Returns information about:
    - current goal and phase
    - pending workflow/clarification state
    - visibility/session diagnostics
    - router statistics and component status
    - Bounded repair guidance when the latest router state indicates a failure/recovery path
    """
    session = await get_session_capability_state_async(ctx)
    surface_profile = session.surface_profile or get_config().MCP_SURFACE_PROFILE
    contract_line = session.contract_version or _get_runtime_contract_line(ctx)
    diagnostics = build_visibility_diagnostics(surface_profile, session.phase)
    status_payload = get_router_status()
    background_job_count, background_job_counts_by_status, background_jobs = _build_background_job_diagnostics()
    status_payload.update(
        {
            "current_goal": session.goal,
            "current_phase": session.phase.value,
            "surface_profile": surface_profile,
            "contract_version": contract_line,
            "pending_clarification": session.pending_clarification,
            "pending_question_set_id": session.pending_question_set_id,
            "partial_answers": session.partial_answers,
            "last_elicitation_action": session.last_elicitation_action,
            "last_router_status": session.last_router_status,
            "last_router_disposition": session.last_router_disposition,
            "last_router_error": session.last_router_error,
            "policy_context": session.policy_context,
            "visibility_rules": [dict(rule) for rule in diagnostics.rules],
            "visible_capabilities": list(diagnostics.visible_capability_ids),
            "visible_entry_capabilities": list(diagnostics.visible_entry_capability_ids),
            "hidden_capability_count": len(diagnostics.hidden_capability_ids),
            "hidden_category_counts": diagnostics.hidden_category_counts,
            "router_failure_policy": "fail_closed" if surface_profile != "legacy-flat" else "fail_open",
            "timeout_policy": _build_timeout_policy_diagnostics(ctx),
            "task_runtime": _build_task_runtime_diagnostics(ctx),
            "telemetry": _build_telemetry_diagnostics(),
            "list_page_size": _get_list_page_size(ctx),
            "background_job_count": background_job_count,
            "background_job_counts_by_status": background_job_counts_by_status,
            "background_jobs": background_jobs,
            "reference_image_count": len(session.reference_images or []),
            "reference_images": list(session.reference_images or []),
        }
    )
    if _should_attach_repair_suggestion(status_payload):
        repair_outcome = await run_repair_suggestion_assistant(
            ctx,
            diagnostics=_build_repair_diagnostics(status_payload, source="router_get_status"),
        )
        status_payload["repair_suggestion"] = to_repair_assistant_contract(repair_outcome).model_dump()
    return RouterStatusContract.model_validate(status_payload)


async def router_clear_goal(ctx: Context) -> str:
    """
    [SYSTEM][SAFE] Clear the current modeling goal.

    Use this when you've finished building one object and want to start
    a new one with a different workflow.
    """
    handler = get_router_handler()
    result = handler.clear_goal()
    state = await clear_session_goal_state_async(
        ctx,
        surface_profile=get_config().MCP_SURFACE_PROFILE,
        contract_version=_get_runtime_contract_line(ctx),
    )
    await apply_visibility_for_session_state(ctx, state)
    ctx_info(ctx, "[ROUTER] Goal cleared")
    return result


# --- Semantic Matching Tools (TASK-046) ---


def router_find_similar_workflows(
    ctx: Context,
    prompt: str,
    top_k: int = 5,
) -> str:
    """
    [SYSTEM][SAFE] Find workflows similar to a description.

    Uses LaBSE semantic embeddings to find workflows that match
    the meaning of your prompt, not just keywords.

    Useful for:
    - Exploring available workflows
    - Finding the right workflow for an object
    - Understanding what workflows could apply

    Args:
        prompt: Description of what you want to build.
        top_k: Number of similar workflows to return.

    Returns:
        Formatted list of similar workflows with similarity scores.

    Example:
        router_find_similar_workflows("comfortable office chair")
        -> 1. chair_workflow: ████████████████░░░░ 85.0%
           2. table_workflow: ████████████░░░░░░░░ 62.0%
    """
    handler = cast(Any, get_router_handler())
    return handler.find_similar_workflows_formatted(prompt, top_k)


def router_get_inherited_proportions(
    ctx: Context,
    workflow_names: List[str],
    dimensions: Optional[List[float]] = None,
) -> str:
    """
    [SYSTEM][SAFE] Get inherited proportions from similar workflows.

    Combines proportion rules from multiple workflows.
    Useful for objects that don't have their own workflow.

    Args:
        workflow_names: List of workflow names to inherit from.
        dimensions: Optional object dimensions [x, y, z] in meters.

    Returns:
        Formatted proportions with values.

    Example:
        router_get_inherited_proportions(
            ["table_workflow", "chair_workflow"],
            [0.5, 0.5, 0.9]
        )
    """
    handler = cast(Any, get_router_handler())
    return handler.get_proportions_formatted(workflow_names, dimensions)


def router_feedback(
    ctx: Context,
    prompt: str,
    correct_workflow: str,
) -> str:
    """
    [SYSTEM][SAFE] Provide feedback to improve workflow matching.

    Call this when the router matched the wrong workflow.
    The feedback is stored and used to improve future matching.

    Args:
        prompt: The original prompt/description.
        correct_workflow: The workflow that should have matched.

    Returns:
        Confirmation message.

    Example:
        # Router matched "phone_workflow" but you wanted "tablet_workflow"
        router_feedback("create a large tablet", "tablet_workflow")
    """
    handler = get_router_handler()
    result = handler.record_feedback(prompt, correct_workflow)
    ctx_info(ctx, f"[ROUTER] Feedback recorded: {prompt[:30]}... -> {correct_workflow}")
    return result

    # TASK-055-FIX: Removed separate parameter resolution tools.
    # All parameter resolution now happens through router_set_goal with resolved_params argument.
