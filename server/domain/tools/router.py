"""
Router Tool Interface.

Abstract interface for Router Supervisor control tools.
These are meta-tools that control the router's behavior, not Blender operations.

TASK-046: Extended with semantic matching methods.
TASK-055: Extended with parameter resolution methods.
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

    # --- Parameter Resolution Methods (TASK-055) ---

    @abstractmethod
    def store_parameter_value(
        self,
        context: str,
        parameter_name: str,
        value: Any,
        workflow_name: str,
    ) -> str:
        """Store a resolved parameter value for future reuse.

        Called by LLM after resolving an unresolved parameter.
        The value is validated against the parameter schema if available.

        Args:
            context: The natural language context that triggered this value
                    (e.g., "straight legs", "wide table").
            parameter_name: Name of the parameter being resolved.
            value: The resolved value (must match parameter type/range).
            workflow_name: Name of the workflow this parameter belongs to.

        Returns:
            Confirmation message or error message if validation fails.
        """
        pass

    @abstractmethod
    def list_parameter_mappings(
        self,
        workflow_name: Optional[str] = None,
    ) -> str:
        """List stored parameter mappings.

        Args:
            workflow_name: Optional filter by workflow name.

        Returns:
            Formatted list of stored mappings.
        """
        pass

    @abstractmethod
    def delete_parameter_mapping(
        self,
        context: str,
        parameter_name: str,
        workflow_name: str,
    ) -> str:
        """Delete a stored parameter mapping.

        Args:
            context: The context string of the mapping to delete.
            parameter_name: Parameter name.
            workflow_name: Workflow name.

        Returns:
            Confirmation or error message.
        """
        pass

    @abstractmethod
    def set_goal_interactive(
        self,
        goal: str,
    ) -> Dict[str, Any]:
        """Set goal with interactive parameter resolution.

        Similar to set_goal, but returns detailed information about
        unresolved parameters that need LLM/user input.

        Args:
            goal: User's modeling goal.

        Returns:
            Dictionary with:
            - workflow_name: Matched workflow (or None)
            - resolved_parameters: Parameters already resolved
            - unresolved_parameters: Parameters needing LLM input
            - resolution_sources: How each parameter was resolved
        """
        pass
