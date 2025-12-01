"""
Workflow Expansion Engine Interface.

Abstract interface for expanding tool calls into workflows.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from server.router.domain.entities.tool_call import CorrectedToolCall
from server.router.domain.entities.scene_context import SceneContext
from server.router.domain.entities.pattern import DetectedPattern


class IExpansionEngine(ABC):
    """Abstract interface for workflow expansion.

    Transforms single tool calls into multi-step workflows.
    """

    @abstractmethod
    def expand(
        self,
        tool_name: str,
        params: Dict[str, Any],
        context: SceneContext,
        pattern: Optional[DetectedPattern] = None,
    ) -> Optional[List[CorrectedToolCall]]:
        """Expand a tool call into a workflow if applicable.

        Args:
            tool_name: Name of the tool to potentially expand.
            params: Original parameters.
            context: Current scene context.
            pattern: Detected geometry pattern (if any).

        Returns:
            List of expanded tool calls, or None if no expansion.
        """
        pass

    @abstractmethod
    def get_workflow(self, workflow_name: str) -> Optional[List[Dict[str, Any]]]:
        """Get a workflow definition by name.

        Args:
            workflow_name: Name of the workflow.

        Returns:
            Workflow steps definition, or None if not found.
        """
        pass

    @abstractmethod
    def register_workflow(
        self,
        name: str,
        steps: List[Dict[str, Any]],
        trigger_pattern: Optional[str] = None,
        trigger_keywords: Optional[List[str]] = None,
    ) -> None:
        """Register a new workflow.

        Args:
            name: Unique workflow name.
            steps: List of workflow steps.
            trigger_pattern: Pattern that triggers this workflow.
            trigger_keywords: Keywords that trigger this workflow.
        """
        pass

    @abstractmethod
    def get_available_workflows(self) -> List[str]:
        """Get names of all registered workflows.

        Returns:
            List of workflow names.
        """
        pass

    @abstractmethod
    def expand_workflow(
        self,
        workflow_name: str,
        params: Dict[str, Any],
    ) -> List[CorrectedToolCall]:
        """Expand a named workflow with parameters.

        Args:
            workflow_name: Name of the workflow to expand.
            params: Parameters to pass to workflow steps.

        Returns:
            List of expanded tool calls.
        """
        pass
