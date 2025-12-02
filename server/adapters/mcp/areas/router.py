"""
Router MCP Tools.

Tools for interacting with the Router Supervisor system.
These tools allow the LLM to communicate its intent to the router.

Follows Clean Architecture pattern:
- MCP adapter layer calls Application layer (RouterToolHandler)
- Handler implements Domain interface (IRouterTool)
"""

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
