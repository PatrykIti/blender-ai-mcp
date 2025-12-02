"""
Workflow Expansion Engine Implementation.

Transforms single tool calls into multi-step workflows.
"""

from typing import Dict, Any, Optional, List

from server.router.domain.interfaces.i_expansion_engine import IExpansionEngine
from server.router.domain.entities.tool_call import CorrectedToolCall
from server.router.domain.entities.scene_context import SceneContext
from server.router.domain.entities.pattern import DetectedPattern
from server.router.infrastructure.config import RouterConfig


class WorkflowExpansionEngine(IExpansionEngine):
    """Implementation of workflow expansion.

    Transforms single tool calls into multi-step workflows.
    Uses WorkflowRegistry as the source of workflows.
    """

    def __init__(self, config: Optional[RouterConfig] = None):
        """Initialize expansion engine.

        Args:
            config: Router configuration (uses defaults if None).
        """
        self._config = config or RouterConfig()
        self._registry = None  # Lazy-loaded

    def _get_registry(self):
        """Get or create the workflow registry.

        Returns:
            WorkflowRegistry instance.
        """
        if self._registry is None:
            from server.router.application.workflows.registry import get_workflow_registry
            self._registry = get_workflow_registry()
        return self._registry

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
        if not self._config.enable_workflow_expansion:
            return None

        registry = self._get_registry()

        # Check if pattern suggests a workflow
        if pattern and pattern.suggested_workflow:
            workflow_name = pattern.suggested_workflow
            if registry.get_definition(workflow_name):
                return self.expand_workflow(workflow_name, params)

        return None

    def get_workflow(self, workflow_name: str) -> Optional[List[Dict[str, Any]]]:
        """Get a workflow definition by name.

        Args:
            workflow_name: Name of the workflow.

        Returns:
            Workflow steps definition, or None if not found.
        """
        registry = self._get_registry()
        definition = registry.get_definition(workflow_name)
        if definition:
            return [{"tool": s.tool, "params": s.params} for s in definition.steps]
        return None

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
        from server.router.application.workflows.base import WorkflowDefinition, WorkflowStep

        workflow_steps = [
            WorkflowStep(tool=s["tool"], params=s.get("params", {}))
            for s in steps
        ]

        definition = WorkflowDefinition(
            name=name,
            description=f"Custom workflow: {name}",
            steps=workflow_steps,
            trigger_pattern=trigger_pattern,
            trigger_keywords=trigger_keywords or [],
        )

        registry = self._get_registry()
        registry.register_definition(definition)

    def get_available_workflows(self) -> List[str]:
        """Get names of all registered workflows.

        Returns:
            List of workflow names.
        """
        registry = self._get_registry()
        return registry.get_all_workflows()

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
        registry = self._get_registry()

        # Use registry's expand_workflow which handles both built-in and custom
        calls = registry.expand_workflow(workflow_name, params)

        # If registry returned calls, resolve any $param references
        if calls:
            for call in calls:
                call.params = self._resolve_step_params(call.params, params)

        return calls

    def _resolve_step_params(
        self,
        step_params: Dict[str, Any],
        original_params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Resolve step parameters with inheritance.

        Args:
            step_params: Parameters defined in workflow step.
            original_params: Original parameters from LLM call.

        Returns:
            Resolved parameters dictionary.
        """
        resolved = {}

        for key, value in step_params.items():
            if isinstance(value, str) and value.startswith("$"):
                # Inherit from original params
                orig_key = value[1:]
                if orig_key in original_params:
                    resolved[key] = original_params[orig_key]
                # Skip if not found in original (use defaults)
            else:
                resolved[key] = value

        return resolved

    def get_workflow_for_pattern(
        self,
        pattern: DetectedPattern,
    ) -> Optional[str]:
        """Get workflow name for a detected pattern.

        Args:
            pattern: Detected geometry pattern.

        Returns:
            Workflow name or None.
        """
        registry = self._get_registry()
        return registry.find_by_pattern(pattern.name)

    def get_workflow_for_keywords(
        self,
        keywords: List[str],
    ) -> Optional[str]:
        """Find workflow matching keywords.

        Args:
            keywords: Keywords to match.

        Returns:
            Workflow name or None.
        """
        registry = self._get_registry()
        # Combine keywords into text for search
        text = " ".join(keywords)
        return registry.find_by_keywords(text)
