"""
Router Tool Interface.

Abstract interface for Router Supervisor control tools.
These are meta-tools that control the router's behavior, not Blender operations.

TASK-046: Extended with semantic matching methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple


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

    # --- Semantic Matching Methods (TASK-046) ---

    @abstractmethod
    def find_similar_workflows(
        self,
        prompt: str,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """Find workflows similar to a prompt.

        Uses LaBSE semantic embeddings to find workflows that match
        the meaning of the prompt, not just keywords.

        Args:
            prompt: Description of what to build.
            top_k: Number of similar workflows to return.

        Returns:
            List of (workflow_name, similarity) tuples.
        """
        pass

    @abstractmethod
    def get_inherited_proportions(
        self,
        workflow_names: List[str],
        dimensions: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Get inherited proportions from workflows.

        Combines proportion rules from multiple workflows.

        Args:
            workflow_names: List of workflow names to inherit from.
            dimensions: Optional object dimensions [x, y, z].

        Returns:
            Dictionary with inherited proportion data.
        """
        pass

    @abstractmethod
    def record_feedback(
        self,
        prompt: str,
        correct_workflow: str,
    ) -> str:
        """Record user feedback for workflow matching.

        Call this when the router matched the wrong workflow.

        Args:
            prompt: Original prompt/description.
            correct_workflow: The workflow that should have matched.

        Returns:
            Confirmation message.
        """
        pass

    @abstractmethod
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """Get feedback statistics.

        Returns:
            Dictionary with feedback statistics.
        """
        pass
