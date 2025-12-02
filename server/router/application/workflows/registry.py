"""
Workflow Registry.

Central registry for all available workflows.
"""

import logging
from typing import Dict, Any, Optional, List

from .base import BaseWorkflow, WorkflowDefinition, WorkflowStep
from .phone_workflow import phone_workflow
from .tower_workflow import tower_workflow
from .screen_cutout_workflow import screen_cutout_workflow
from server.router.domain.entities.tool_call import CorrectedToolCall

logger = logging.getLogger(__name__)


class WorkflowRegistry:
    """Central registry for all workflows.

    Manages both built-in and custom workflows, providing unified
    access and lookup methods.
    """

    def __init__(self):
        """Initialize registry with built-in workflows."""
        self._workflows: Dict[str, BaseWorkflow] = {}
        self._custom_definitions: Dict[str, WorkflowDefinition] = {}
        self._custom_loaded: bool = False

        # Register built-in workflows
        self._register_builtin(phone_workflow)
        self._register_builtin(tower_workflow)
        self._register_builtin(screen_cutout_workflow)

    def _register_builtin(self, workflow: BaseWorkflow) -> None:
        """Register a built-in workflow.

        Args:
            workflow: Workflow instance to register.
        """
        self._workflows[workflow.name] = workflow

    def register_workflow(self, workflow: BaseWorkflow) -> None:
        """Register a workflow.

        Args:
            workflow: Workflow to register.
        """
        self._workflows[workflow.name] = workflow

    def register_definition(self, definition: WorkflowDefinition) -> None:
        """Register a workflow from definition.

        Args:
            definition: Workflow definition to register.
        """
        self._custom_definitions[definition.name] = definition

    def load_custom_workflows(self, reload: bool = False) -> int:
        """Load custom workflows from YAML/JSON files.

        Uses WorkflowLoader to load workflows from the custom workflows
        directory and registers them in this registry.

        Args:
            reload: If True, reload even if already loaded.

        Returns:
            Number of workflows loaded.
        """
        if self._custom_loaded and not reload:
            return len(self._custom_definitions)

        from server.router.infrastructure.workflow_loader import get_workflow_loader

        loader = get_workflow_loader()

        if reload:
            workflows = loader.reload()
        else:
            workflows = loader.load_all()

        # Register all loaded workflows
        count = 0
        for name, definition in workflows.items():
            self._custom_definitions[name] = definition
            count += 1
            logger.debug(f"Registered custom workflow: {name}")

        self._custom_loaded = True
        logger.info(f"Loaded {count} custom workflows into registry")
        return count

    def ensure_custom_loaded(self) -> None:
        """Ensure custom workflows are loaded (lazy loading)."""
        if not self._custom_loaded:
            self.load_custom_workflows()

    def get_workflow(self, name: str) -> Optional[BaseWorkflow]:
        """Get a workflow by name.

        Args:
            name: Workflow name.

        Returns:
            Workflow instance or None.
        """
        return self._workflows.get(name)

    def get_definition(self, name: str) -> Optional[WorkflowDefinition]:
        """Get a workflow definition by name.

        Args:
            name: Workflow name.

        Returns:
            Workflow definition or None.
        """
        # Check custom definitions first
        if name in self._custom_definitions:
            return self._custom_definitions[name]

        # Check built-in workflows
        workflow = self._workflows.get(name)
        if workflow:
            return workflow.get_definition()

        return None

    def get_all_workflows(self) -> List[str]:
        """Get all registered workflow names.

        Returns:
            List of workflow names.
        """
        # Ensure custom workflows are loaded
        self.ensure_custom_loaded()

        all_names = set(self._workflows.keys())
        all_names.update(self._custom_definitions.keys())
        return sorted(all_names)

    def find_by_pattern(self, pattern_name: str) -> Optional[str]:
        """Find workflow matching a pattern.

        Args:
            pattern_name: Detected pattern name.

        Returns:
            Workflow name or None.
        """
        # Ensure custom workflows are loaded
        self.ensure_custom_loaded()

        # Check built-in workflows
        for name, workflow in self._workflows.items():
            if workflow.matches_pattern(pattern_name):
                return name

        # Check custom definitions
        for name, definition in self._custom_definitions.items():
            if definition.trigger_pattern == pattern_name:
                return name

        return None

    def find_by_keywords(self, text: str) -> Optional[str]:
        """Find workflow matching keywords in text.

        Args:
            text: Text to search for keywords.

        Returns:
            Workflow name or None.
        """
        # Ensure custom workflows are loaded
        self.ensure_custom_loaded()

        text_lower = text.lower()

        # Check built-in workflows
        for name, workflow in self._workflows.items():
            if workflow.matches_keywords(text_lower):
                return name

        # Check custom definitions
        for name, definition in self._custom_definitions.items():
            for keyword in definition.trigger_keywords:
                if keyword.lower() in text_lower:
                    return name

        return None

    def expand_workflow(
        self,
        workflow_name: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[CorrectedToolCall]:
        """Expand a workflow into tool calls.

        Args:
            workflow_name: Name of workflow to expand.
            params: Optional parameters to customize workflow.

        Returns:
            List of tool calls to execute.
        """
        # Ensure custom workflows are loaded
        self.ensure_custom_loaded()

        # Try built-in workflow first
        workflow = self._workflows.get(workflow_name)
        if workflow:
            steps = workflow.get_steps(params)
            return self._steps_to_calls(steps, workflow_name)

        # Try custom definition
        definition = self._custom_definitions.get(workflow_name)
        if definition:
            steps = self._resolve_definition_params(definition.steps, params or {})
            return self._steps_to_calls(steps, workflow_name)

        return []

    def _steps_to_calls(
        self,
        steps: List[WorkflowStep],
        workflow_name: str,
    ) -> List[CorrectedToolCall]:
        """Convert workflow steps to corrected tool calls.

        Args:
            steps: Workflow steps.
            workflow_name: Name of the workflow.

        Returns:
            List of tool calls.
        """
        calls = []
        for i, step in enumerate(steps):
            call = CorrectedToolCall(
                tool_name=step.tool,
                params=dict(step.params),
                corrections_applied=[f"workflow:{workflow_name}:step_{i+1}"],
                is_injected=True,
            )
            calls.append(call)
        return calls

    def _resolve_definition_params(
        self,
        steps: List[WorkflowStep],
        params: Dict[str, Any],
    ) -> List[WorkflowStep]:
        """Resolve parameter references in workflow steps.

        Args:
            steps: Original workflow steps.
            params: Parameters to substitute.

        Returns:
            Steps with resolved parameters.
        """
        resolved_steps = []

        for step in steps:
            resolved_params = {}
            for key, value in step.params.items():
                if isinstance(value, str) and value.startswith("$"):
                    param_name = value[1:]
                    if param_name in params:
                        resolved_params[key] = params[param_name]
                    # Skip if param not found (use defaults from tool)
                else:
                    resolved_params[key] = value

            resolved_steps.append(
                WorkflowStep(
                    tool=step.tool,
                    params=resolved_params,
                    description=step.description,
                    condition=step.condition,
                )
            )

        return resolved_steps

    def get_workflow_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed info about a workflow.

        Args:
            name: Workflow name.

        Returns:
            Dictionary with workflow info.
        """
        # Check built-in
        workflow = self._workflows.get(name)
        if workflow:
            return {
                "name": workflow.name,
                "description": workflow.description,
                "type": "builtin",
                "trigger_pattern": workflow.trigger_pattern,
                "trigger_keywords": workflow.trigger_keywords,
                "step_count": len(workflow.get_steps()),
            }

        # Check custom
        definition = self._custom_definitions.get(name)
        if definition:
            return {
                "name": definition.name,
                "description": definition.description,
                "type": "custom",
                "category": definition.category,
                "author": definition.author,
                "version": definition.version,
                "trigger_pattern": definition.trigger_pattern,
                "trigger_keywords": definition.trigger_keywords,
                "step_count": len(definition.steps),
            }

        return None


# Global registry singleton
_registry: Optional[WorkflowRegistry] = None


def get_workflow_registry() -> WorkflowRegistry:
    """Get the global workflow registry.

    Returns:
        WorkflowRegistry singleton.
    """
    global _registry
    if _registry is None:
        _registry = WorkflowRegistry()
    return _registry
