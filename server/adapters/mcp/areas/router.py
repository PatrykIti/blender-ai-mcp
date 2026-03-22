"""
Router MCP Tools.

Tools for interacting with the Router Supervisor system.
These tools allow the LLM to communicate its intent to the router.

Follows Clean Architecture pattern:
- MCP adapter layer calls Application layer (RouterToolHandler)
- Handler implements Domain interface (IRouterTool)

TASK-046: Extended with semantic matching tools.
TASK-055-FIX: Unified parameter resolution through single router_set_goal tool.
"""

import json
from typing import Any, Dict, List, Optional
from fastmcp import Context
from fastmcp.server.context import AcceptedElicitation, CancelledElicitation, DeclinedElicitation
from server.adapters.mcp.contracts.router import (
    RouterGoalResponseContract,
    RouterStatusContract,
)
from server.adapters.mcp.elicitation_contracts import (
    build_clarification_plan,
    build_elicitation_response_type,
    build_fallback_payload,
    coerce_elicitation_answers,
)
from server.adapters.mcp.session_capabilities import (
    clear_session_goal_state,
    update_session_from_router_goal,
)
from server.adapters.mcp.instance import mcp
from server.adapters.mcp.visibility.tags import get_capability_tags
from server.adapters.mcp.context_utils import ctx_info
from server.adapters.mcp.router_helper import get_router_status
from server.infrastructure.config import get_config
from server.infrastructure.di import get_router_handler

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

    return {
        tool_name: _register_existing_tool(target, tool_name)
        for tool_name in ROUTER_PUBLIC_TOOL_NAMES
    }


async def _maybe_elicit_router_answers(
    ctx: Context,
    goal: str,
    result: Dict[str, Any],
) -> Dict[str, Any]:
    """Attempt native FastMCP elicitation for missing router parameters."""

    if get_config().MCP_SURFACE_PROFILE != "llm-guided":
        return result

    if result.get("status") != "needs_input":
        return result

    plan = build_clarification_plan(
        goal=goal,
        workflow_name=result.get("workflow") or "unknown_workflow",
        unresolved_fields=result.get("unresolved", []),
    )
    if plan.is_empty:
        return result

    fallback_payload = build_fallback_payload(plan)
    result["clarification"] = fallback_payload.model_dump()

    try:
        response = await ctx.elicit(
            message=f"Missing parameters for workflow '{plan.workflow_name}'",
            response_type=build_elicitation_response_type(plan),
        )
    except Exception:
        result["elicitation_action"] = "unavailable"
        return result

    if isinstance(response, AcceptedElicitation):
        result["elicitation_action"] = "accept"
        result["elicitation_answers"] = coerce_elicitation_answers(response.data)
    elif isinstance(response, DeclinedElicitation):
        result["elicitation_action"] = "decline"
    elif isinstance(response, CancelledElicitation):
        result["elicitation_action"] = "cancel"

    return result


@mcp.tool()
async def router_set_goal(
    ctx: Context,
    goal: str,
    resolved_params: Optional[Dict[str, Any]] = None,
) -> RouterGoalResponseContract:
    """
    [SYSTEM][CRITICAL] Tell the Router what you're building.

    IMPORTANT: Call this FIRST before ANY modeling operation!

    This is the ONLY tool needed for workflow interaction:
    1. First call: Set goal, Router matches workflow and resolves parameters
    2. If unresolved params exist: Returns questions for you to answer
    3. Second call: Provide resolved_params dict, Router stores and executes

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
    result = handler.set_goal(goal, resolved_params)

    if resolved_params is None and result.get("status") == "needs_input":
        result = await _maybe_elicit_router_answers(ctx, goal, result)
        if result.get("elicitation_action") == "accept":
            result = handler.set_goal(
                goal,
                resolved_params=result.get("elicitation_answers"),
            )

    update_session_from_router_goal(ctx, goal, result)

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

    if result.get("status") == "needs_input" and "clarification" not in result:
        plan = build_clarification_plan(
            goal=goal,
            workflow_name=result.get("workflow") or "unknown_workflow",
            unresolved_fields=result.get("unresolved", []),
        )
        if not plan.is_empty:
            result["clarification"] = build_fallback_payload(plan).model_dump()

    return RouterGoalResponseContract.model_validate(result)


@mcp.tool()
def router_get_status(ctx: Context) -> RouterStatusContract:
    """
    [SYSTEM][SAFE] Get current Router Supervisor status.

    Returns information about:
    - Current goal (if set)
    - Pending workflow
    - Router statistics
    - Component status
    """
    return RouterStatusContract.model_validate(get_router_status())


@mcp.tool()
def router_clear_goal(ctx: Context) -> str:
    """
    [SYSTEM][SAFE] Clear the current modeling goal.

    Use this when you've finished building one object and want to start
    a new one with a different workflow.
    """
    handler = get_router_handler()
    result = handler.clear_goal()
    clear_session_goal_state(ctx)
    ctx_info(ctx, "[ROUTER] Goal cleared")
    return result


# --- Semantic Matching Tools (TASK-046) ---


@mcp.tool()
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
    handler = get_router_handler()
    return handler.find_similar_workflows_formatted(prompt, top_k)


@mcp.tool()
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
    handler = get_router_handler()
    return handler.get_proportions_formatted(workflow_names, dimensions)


@mcp.tool()
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
