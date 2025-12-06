"""
Router MCP Tools.

Tools for interacting with the Router Supervisor system.
These tools allow the LLM to communicate its intent to the router.

Follows Clean Architecture pattern:
- MCP adapter layer calls Application layer (RouterToolHandler)
- Handler implements Domain interface (IRouterTool)

TASK-046: Extended with semantic matching tools.
"""

from typing import List, Optional
from fastmcp import Context
from server.adapters.mcp.instance import mcp
from server.infrastructure.di import get_router_handler


@mcp.tool()
def router_set_goal(ctx: Context, goal: str) -> str:
    """
    [SYSTEM][CRITICAL] Tell the Router what you're building.

    IMPORTANT: Call this FIRST before ANY modeling operation!

    The Router Supervisor uses this to optimize your workflow automatically.
    Without setting a goal, the router cannot help you with smart workflow
    expansion and error prevention.

    Args:
        goal: What you're creating. Be specific!
              Examples: "smartphone", "wooden table", "medieval tower",
                       "office chair", "sports car", "human face"

    Returns:
        Confirmation with matched workflow (if any).

    Example workflow:
        1. router_set_goal("smartphone")     # <- FIRST!
        2. modeling_create_primitive("CUBE") # Router expands to phone workflow
        3. ... router handles the rest automatically

    Supported goal keywords (trigger workflows):
        - phone, smartphone, tablet, mobile -> phone_workflow
        - tower, pillar, column, obelisk -> tower_workflow
        - table, desk, surface -> table_workflow
        - house, building, home -> house_workflow
        - chair, seat, stool -> chair_workflow
    """
    handler = get_router_handler()
    result = handler.set_goal(goal)

    # Log to context if workflow matched
    if "Matched workflow:" in result:
        ctx.info(f"[ROUTER] Goal set: {goal} -> workflow matched")
    else:
        ctx.info(f"[ROUTER] Goal set: {goal} (no matching workflow)")

    return result


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
    ctx.info("[ROUTER] Goal cleared")
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
    ctx.info(f"[ROUTER] Feedback recorded: {prompt[:30]}... -> {correct_workflow}")
    return result
