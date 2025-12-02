"""
Router Tool Interface.

Abstract interface for Router Supervisor control tools.
These are meta-tools that control the router's behavior, not Blender operations.
"""

from abc import ABC, abstractmethod
from typing import Optional


class IRouterTool(ABC):
    """Interface for Router control tools.

    These tools allow the LLM to communicate its intent to the Router Supervisor.
    Unlike other tools, these do NOT send RPC commands to Blender - they only
    manage internal router state.

    Methods:
        set_goal: Set the current modeling goal.
        get_status: Get router status and statistics.
        clear_goal: Clear the current goal.
        get_goal: Get the current goal.
        get_pending_workflow: Get the workflow matched from goal.
    """

    @abstractmethod
    def set_goal(self, goal: str) -> str:
        """Set current modeling goal.

        Args:
            goal: User's modeling goal (e.g., "smartphone", "table")

        Returns:
            Confirmation message with matched workflow (if any).
        """
        pass

    @abstractmethod
    def get_status(self) -> str:
        """Get router status and statistics.

        Returns:
            Formatted status string with goal, workflow, stats, and components.
        """
        pass

    @abstractmethod
    def clear_goal(self) -> str:
        """Clear current modeling goal.

        Returns:
            Confirmation message.
        """
        pass

    @abstractmethod
    def get_goal(self) -> Optional[str]:
        """Get current modeling goal.

        Returns:
            Current goal or None.
        """
        pass

    @abstractmethod
    def get_pending_workflow(self) -> Optional[str]:
        """Get workflow matched from current goal.

        Returns:
            Workflow name or None.
        """
        pass

    @abstractmethod
    def is_enabled(self) -> bool:
        """Check if router is enabled.

        Returns:
            True if router is enabled and ready.
        """
        pass
