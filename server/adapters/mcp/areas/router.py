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
from server.adapters.mcp.instance import mcp
from server.adapters.mcp.context_utils import ctx_info
from server.infrastructure.di import get_router_handler


@mcp.tool()
def router_set_goal(
    ctx: Context,
    goal: str,
    resolved_params: Optional[Dict[str, Any]] = None,
) -> str:
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

    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool()
def router_get_status(ctx: Context) -> str:
    """
    [SYSTEM][SAFE] Get current Router Supervisor status.

    Returns information about:
    - Current goal (if set)
    - Pending workflow
    - Router statistics
    - Component status
    """
    handler = get_router_handler()
    return handler.get_status()


@mcp.tool()
def router_clear_goal(ctx: Context) -> str:
    """
    [SYSTEM][SAFE] Clear the current modeling goal.

    Use this when you've finished building one object and want to start
    a new one with a different workflow.
    """
    handler = get_router_handler()
    result = handler.clear_goal()
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
