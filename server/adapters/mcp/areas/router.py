"""
Router MCP Tools.

Tools for interacting with the Router Supervisor system.
These tools allow the LLM to communicate its intent to the router.

Follows Clean Architecture pattern:
- MCP adapter layer calls Application layer (RouterToolHandler)
- Handler implements Domain interface (IRouterTool)

TASK-046: Extended with semantic matching tools.
TASK-055: Extended with parameter resolution tools.
"""

from typing import List, Optional, Union
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


# --- Parameter Resolution Tools (TASK-055) ---


@mcp.tool()
def router_store_parameter(
    ctx: Context,
    context: str,
    parameter_name: str,
    value: Union[float, int, bool, str],
    workflow_name: str,
) -> str:
    """
    [SYSTEM][SAFE] Store a resolved parameter value for future reuse.

    Use this tool after the LLM has resolved an unresolved parameter
    to store the mapping for future similar prompts.

    The router learns from these mappings using semantic similarity (LaBSE).
    When a similar prompt is encountered in the future, the stored value
    will be automatically reused.

    Args:
        context: The natural language phrase that triggered this value.
                 Should be the relevant part of the user's prompt.
                 Examples: "straight legs", "wide table", "nogi proste"
        parameter_name: Name of the workflow parameter being resolved.
                       Example: "leg_angle_left", "top_width"
        value: The resolved value. Must match the parameter's type and range.
               Example: 0.0 for straight legs, 2.5 for wide table
        workflow_name: Name of the workflow this parameter belongs to.
                      Example: "picnic_table"

    Returns:
        Confirmation message or error if validation fails.

    Example:
        # After user says "create a table with straight legs"
        # and LLM decides leg_angle should be 0:
        router_store_parameter(
            context="straight legs",
            parameter_name="leg_angle_left",
            value=0.0,
            workflow_name="picnic_table"
        )
    """
    handler = get_router_handler()
    result = handler.store_parameter_value(
        context=context,
        parameter_name=parameter_name,
        value=value,
        workflow_name=workflow_name,
    )
    ctx.info(f"[ROUTER] Parameter stored: {context} -> {parameter_name}={value}")
    return result


@mcp.tool()
def router_list_parameters(
    ctx: Context,
    workflow_name: Optional[str] = None,
) -> str:
    """
    [SYSTEM][SAFE][READ-ONLY] List stored parameter mappings.

    Shows all learned parameter values that have been stored for reuse.
    Useful for debugging or understanding what the router has learned.

    Args:
        workflow_name: Optional filter by workflow name.
                      If not provided, shows all mappings.

    Returns:
        Formatted list of stored parameter mappings grouped by workflow.
    """
    handler = get_router_handler()
    return handler.list_parameter_mappings(workflow_name=workflow_name)


@mcp.tool()
def router_delete_parameter(
    ctx: Context,
    context: str,
    parameter_name: str,
    workflow_name: str,
) -> str:
    """
    [SYSTEM][DESTRUCTIVE] Delete a stored parameter mapping.

    Use this to remove incorrect or outdated learned parameter values.

    Args:
        context: The context string of the mapping to delete.
        parameter_name: Parameter name.
        workflow_name: Workflow name.

    Returns:
        Confirmation or error message.

    Example:
        # Remove an incorrect mapping
        router_delete_parameter(
            context="straight legs",
            parameter_name="leg_angle_left",
            workflow_name="picnic_table"
        )
    """
    handler = get_router_handler()
    result = handler.delete_parameter_mapping(
        context=context,
        parameter_name=parameter_name,
        workflow_name=workflow_name,
    )
    ctx.info(f"[ROUTER] Parameter mapping deleted: {context} -> {parameter_name}")
    return result


@mcp.tool()
def router_set_goal_interactive(
    ctx: Context,
    goal: str,
) -> str:
    """
    [SYSTEM][SAFE] Set modeling goal with interactive parameter resolution.

    Enhanced version of router_set_goal that provides detailed feedback about
    which parameters were resolved automatically and which need LLM input.

    This tool uses a three-tier parameter resolution system:
    1. YAML modifiers (highest priority) - from matched workflow definition
    2. Learned mappings (LaBSE embeddings) - from previous LLM resolutions
    3. Unresolved (needs LLM input) - for parameters not found in tiers 1 or 2

    Use this tool when you want to:
    - See exactly which parameters were auto-resolved
    - Know which parameters need interactive input
    - Understand the resolution source for each parameter

    After receiving unresolved parameters, use router_store_parameter() to
    provide values. These values will be learned for future similar prompts.

    Args:
        goal: The user's modeling goal. Be specific with natural language
              modifiers (e.g., "picnic table with straight legs",
              "wide dining table", "stół z prostymi nogami").

    Returns:
        Formatted string showing:
        - Matched workflow name
        - Resolved parameters with their sources
        - Unresolved parameters that need LLM input with schemas

    Example:
        # User says: "create a picnic table with straight legs"
        router_set_goal_interactive("picnic table with straight legs")

        # Returns something like:
        # Matched workflow: picnic_table
        #
        # Resolved parameters:
        #   leg_angle_left = 0.0 (yaml_modifier)
        #   leg_angle_right = 0.0 (yaml_modifier)
        #
        # All parameters resolved! Workflow is ready to execute.

    See also:
        - router_set_goal: Simple goal setting without parameter details
        - router_store_parameter: Store resolved parameter values
        - router_list_parameters: List all learned parameter mappings
    """
    handler = get_router_handler()
    result = handler.set_goal_interactive_formatted(goal)

    # Extract workflow name from result for logging
    if "Matched workflow:" in result:
        ctx.info(f"[ROUTER] Interactive goal set: {goal} (with parameter resolution)")
    else:
        ctx.info(f"[ROUTER] Interactive goal set: {goal} (no workflow matched)")

    return result
