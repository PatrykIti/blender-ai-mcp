"""
Router Tool Handler.

Application layer handler for Router control tools.
Implements IRouterTool interface.
"""

from typing import Optional

from server.domain.tools.router import IRouterTool


class RouterToolHandler(IRouterTool):
    """Handler for Router control tools.

    Unlike other handlers, this does NOT use RPC to communicate with Blender.
    It manages internal Router Supervisor state.

    Attributes:
        _router: SupervisorRouter instance (lazy-loaded).
        _enabled: Whether router is enabled in config.
    """

    def __init__(self, router=None, enabled: bool = True):
        """Initialize router handler.

        Args:
            router: Optional SupervisorRouter instance.
                   If not provided, will be obtained from DI.
            enabled: Whether router is enabled.
        """
        self._router = router
        self._enabled = enabled

    def _get_router(self):
        """Get router instance (lazy loading).

        Returns:
            SupervisorRouter instance or None.
        """
        if self._router is None:
            from server.infrastructure.di import get_router
            self._router = get_router()
        return self._router

    def set_goal(self, goal: str) -> str:
        """Set current modeling goal.

        Args:
            goal: User's modeling goal (e.g., "smartphone", "table")

        Returns:
            Confirmation message with matched workflow (if any).
        """
        if not self._enabled:
            return "Router is disabled. Goal noted but no workflow optimization available."

        router = self._get_router()
        if router is None:
            return "Router not initialized."

        matched_workflow = router.set_current_goal(goal)

        if matched_workflow:
            return (
                f"Goal set: '{goal}'\n"
                f"Matched workflow: {matched_workflow}\n\n"
                f"Proceeding with your next tool call will trigger this workflow automatically."
            )
        else:
            return (
                f"Goal set: '{goal}'\n"
                f"No specific workflow matched. Router will use heuristics to assist.\n\n"
                f"You can proceed with modeling - router will still help with mode switching and error prevention."
            )

    def get_status(self) -> str:
        """Get router status and statistics.

        Returns:
            Formatted status string.
        """
        if not self._enabled:
            return "Router Supervisor is DISABLED.\nSet ROUTER_ENABLED=true to enable."

        router = self._get_router()
        if router is None:
            return "Router not initialized."

        goal = router.get_current_goal()
        stats = router.get_stats()
        components = router.get_component_status()

        lines = [
            "=== Router Supervisor Status ===",
            f"Current goal: {goal or '(not set)'}",
            f"Pending workflow: {router.get_pending_workflow() or '(none)'}",
            "",
            "Statistics:",
            f"  Total calls processed: {stats.get('total_calls', 0)}",
            f"  Corrections applied: {stats.get('corrections_applied', 0)}",
            f"  Workflows expanded: {stats.get('workflows_expanded', 0)}",
            f"  Blocked calls: {stats.get('blocked_calls', 0)}",
            "",
            "Components:",
        ]

        for name, status in components.items():
            status_str = "OK" if status else "NOT READY"
            lines.append(f"  {name}: {status_str}")

        return "\n".join(lines)

    def clear_goal(self) -> str:
        """Clear current modeling goal.

        Returns:
            Confirmation message.
        """
        if not self._enabled:
            return "Router is disabled."

        router = self._get_router()
        if router is None:
            return "Router not initialized."

        router.clear_goal()
        return "Goal cleared. Ready for new modeling task."

    def get_goal(self) -> Optional[str]:
        """Get current modeling goal.

        Returns:
            Current goal or None.
        """
        if not self._enabled:
            return None

        router = self._get_router()
        if router is None:
            return None

        return router.get_current_goal()

    def get_pending_workflow(self) -> Optional[str]:
        """Get workflow matched from current goal.

        Returns:
            Workflow name or None.
        """
        if not self._enabled:
            return None

        router = self._get_router()
        if router is None:
            return None

        return router.get_pending_workflow()

    def is_enabled(self) -> bool:
        """Check if router is enabled.

        Returns:
            True if router is enabled and ready.
        """
        if not self._enabled:
            return False

        router = self._get_router()
        return router is not None
