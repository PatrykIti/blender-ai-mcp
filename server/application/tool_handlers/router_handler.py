"""
Router Tool Handler.

Application layer handler for Router control tools.
Implements IRouterTool interface.

TASK-046: Extended with semantic matching methods.
"""

import json
from typing import Dict, Any, List, Optional, Tuple

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

    # --- Semantic Matching Methods (TASK-046) ---

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
        if not self._enabled:
            return []

        router = self._get_router()
        if router is None:
            return []

        return router.find_similar_workflows(prompt, top_k=top_k)

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
        if not self._enabled:
            return {"error": "Router is disabled"}

        router = self._get_router()
        if router is None:
            return {"error": "Router not initialized"}

        # Convert workflow names to (name, 1.0) tuples for equal weighting
        similar_workflows = [(name, 1.0) for name in workflow_names]

        return router.get_inherited_proportions(similar_workflows, dimensions)

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
        if not self._enabled:
            return "Router is disabled. Feedback not recorded."

        router = self._get_router()
        if router is None:
            return "Router not initialized."

        router.record_feedback_correction(prompt, correct_workflow)

        return (
            f"Feedback recorded. Thank you!\n"
            f"Prompt: '{prompt[:50]}...'\n"
            f"Correct workflow: {correct_workflow}\n\n"
            f"This will help improve future matching."
        )

    def get_feedback_statistics(self) -> Dict[str, Any]:
        """Get feedback statistics.

        Returns:
            Dictionary with feedback statistics.
        """
        if not self._enabled:
            return {"error": "Router is disabled"}

        router = self._get_router()
        if router is None:
            return {"error": "Router not initialized"}

        return router.get_feedback_statistics()

    def find_similar_workflows_formatted(
        self,
        prompt: str,
        top_k: int = 5,
    ) -> str:
        """Find similar workflows and return formatted string.

        Args:
            prompt: Description of what to build.
            top_k: Number of similar workflows to return.

        Returns:
            Formatted string with similar workflows.
        """
        similar = self.find_similar_workflows(prompt, top_k)

        if not similar:
            return (
                f"No similar workflows found for: '{prompt}'\n\n"
                f"This could mean:\n"
                f"- The prompt doesn't match any known workflow patterns\n"
                f"- LaBSE embeddings haven't been loaded yet\n"
                f"- The router is not enabled"
            )

        lines = [
            f"Similar workflows for: '{prompt}'",
            "",
        ]

        for i, (name, score) in enumerate(similar, 1):
            bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
            lines.append(f"{i}. {name}: {bar} {score:.1%}")

        return "\n".join(lines)

    def get_proportions_formatted(
        self,
        workflow_names: List[str],
        dimensions: Optional[List[float]] = None,
    ) -> str:
        """Get inherited proportions and return formatted string.

        Args:
            workflow_names: List of workflow names to inherit from.
            dimensions: Optional object dimensions [x, y, z].

        Returns:
            Formatted string with proportions.
        """
        result = self.get_inherited_proportions(workflow_names, dimensions)

        if "error" in result:
            return result["error"]

        lines = [
            "=== Inherited Proportions ===",
            f"Sources: {', '.join(result.get('sources', []))}",
            f"Total weight: {result.get('total_weight', 0):.2f}",
            "",
            "Proportions:",
        ]

        proportions = result.get("proportions", {})
        for name, value in sorted(proportions.items()):
            lines.append(f"  {name}: {value:.4f}")

        if "applied_values" in result:
            lines.append("")
            lines.append("Applied values (with dimensions):")
            for name, value in sorted(result["applied_values"].items()):
                lines.append(f"  {name}: {value:.4f}")

        return "\n".join(lines)
