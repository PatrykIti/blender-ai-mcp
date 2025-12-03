"""
Workflow Registry.

Central registry for all available workflows.
Supports expression evaluation for $CALCULATE(...) parameters.
Supports conditional step execution.
Supports $AUTO_* proportion-relative parameters.

TASK-041-8: Added ExpressionEvaluator integration
TASK-041-11: Added ConditionEvaluator integration
TASK-041-12: Added context simulation during expansion
TASK-041-14: Added ProportionResolver integration
"""

import logging
from typing import Dict, Any, Optional, List

from .base import BaseWorkflow, WorkflowDefinition, WorkflowStep
from .phone_workflow import phone_workflow
from .tower_workflow import tower_workflow
from .screen_cutout_workflow import screen_cutout_workflow
from server.router.domain.entities.tool_call import CorrectedToolCall
from server.router.application.evaluator.expression_evaluator import ExpressionEvaluator
from server.router.application.evaluator.condition_evaluator import ConditionEvaluator
from server.router.application.evaluator.proportion_resolver import ProportionResolver

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
        self._evaluator = ExpressionEvaluator()
        self._condition_evaluator = ConditionEvaluator()
        self._proportion_resolver = ProportionResolver()

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
        context: Optional[Dict[str, Any]] = None,
    ) -> List[CorrectedToolCall]:
        """Expand a workflow into tool calls.

        Args:
            workflow_name: Name of workflow to expand.
            params: Optional parameters to customize workflow.
            context: Optional context for expression evaluation.
                    Contains dimensions, proportions, mode, etc.

        Returns:
            List of tool calls to execute.
        """
        # Ensure custom workflows are loaded
        self.ensure_custom_loaded()

        # Set up evaluator context
        eval_context = dict(context or {})
        if params:
            eval_context.update(params)
        self._evaluator.set_context(eval_context)

        # Set up condition evaluator context (TASK-041-11)
        condition_context = self._build_condition_context(context or {})
        self._condition_evaluator.set_context(condition_context)

        # Set up proportion resolver (TASK-041-14)
        self._setup_proportion_resolver(context or {})

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

    def _build_condition_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build context for condition evaluation.

        Extracts and normalizes context variables for condition checks.

        Args:
            context: Raw context dictionary.

        Returns:
            Normalized context for condition evaluator.
        """
        condition_context: Dict[str, Any] = {}

        # Mode
        if "mode" in context:
            condition_context["current_mode"] = context["mode"]
        elif "current_mode" in context:
            condition_context["current_mode"] = context["current_mode"]

        # Selection
        if "has_selection" in context:
            condition_context["has_selection"] = context["has_selection"]
        elif "selected_verts" in context:
            # Derive has_selection from vertex count
            condition_context["has_selection"] = context["selected_verts"] > 0

        # Topology info
        for key in ["selected_verts", "selected_edges", "selected_faces",
                    "total_verts", "total_edges", "total_faces"]:
            if key in context:
                condition_context[key] = context[key]

        # Object info
        if "object_count" in context:
            condition_context["object_count"] = context["object_count"]
        if "active_object" in context:
            condition_context["active_object"] = context["active_object"]

        return condition_context

    def _setup_proportion_resolver(self, context: Dict[str, Any]) -> None:
        """Set up proportion resolver with dimensions from context.

        Args:
            context: Context dictionary that may contain dimensions.
        """
        dimensions = None

        # Try to get dimensions from various sources
        if "dimensions" in context:
            dimensions = context["dimensions"]
        elif all(k in context for k in ["width", "height", "depth"]):
            dimensions = [context["width"], context["height"], context["depth"]]

        if dimensions and len(dimensions) >= 3:
            self._proportion_resolver.set_dimensions(dimensions)
            logger.debug(f"ProportionResolver set with dimensions: {dimensions[:3]}")
        else:
            self._proportion_resolver.clear_dimensions()

    def _steps_to_calls(
        self,
        steps: List[WorkflowStep],
        workflow_name: str,
    ) -> List[CorrectedToolCall]:
        """Convert workflow steps to corrected tool calls.

        Evaluates conditions for each step and simulates context updates
        to enable accurate condition evaluation for subsequent steps.

        Args:
            steps: Workflow steps.
            workflow_name: Name of the workflow.

        Returns:
            List of tool calls (skips steps where condition is False).
        """
        calls = []
        skipped_count = 0

        for i, step in enumerate(steps):
            # Check condition if present (TASK-041-11)
            if step.condition:
                should_execute = self._condition_evaluator.evaluate(step.condition)
                if not should_execute:
                    logger.debug(
                        f"Skipping workflow step {i+1} ({step.tool}): "
                        f"condition '{step.condition}' not met"
                    )
                    skipped_count += 1
                    continue

            # Create tool call
            call = CorrectedToolCall(
                tool_name=step.tool,
                params=dict(step.params),
                corrections_applied=[f"workflow:{workflow_name}:step_{i+1}"],
                is_injected=True,
            )
            calls.append(call)

            # Simulate step effect on context (TASK-041-12)
            # This allows subsequent conditions to see updated state
            self._condition_evaluator.simulate_step_effect(step.tool, step.params)

        if skipped_count > 0:
            logger.info(
                f"Workflow '{workflow_name}': {len(calls)} steps to execute, "
                f"{skipped_count} skipped due to conditions"
            )

        return calls

    def _resolve_definition_params(
        self,
        steps: List[WorkflowStep],
        params: Dict[str, Any],
    ) -> List[WorkflowStep]:
        """Resolve parameter references in workflow steps.

        Supports:
        - Simple $variable references (inherit from params)
        - $CALCULATE(...) expressions (evaluate using ExpressionEvaluator)

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
                resolved_value = self._resolve_single_value(value, params)
                # Only add to params if we got a resolved value
                if resolved_value is not None:
                    resolved_params[key] = resolved_value
                elif not isinstance(value, str) or not value.startswith("$"):
                    # Keep non-variable values as-is
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

    def _resolve_single_value(
        self,
        value: Any,
        params: Dict[str, Any],
    ) -> Any:
        """Resolve a single parameter value.

        Args:
            value: Value to resolve.
            params: Available parameters.

        Returns:
            Resolved value or None if unresolvable.
        """
        # Handle list values
        if isinstance(value, list):
            return [self._resolve_single_value(v, params) for v in value]

        # Handle dict values
        if isinstance(value, dict):
            return {k: self._resolve_single_value(v, params) for k, v in value.items()}

        # Handle non-strings
        if not isinstance(value, str):
            return value

        # Check for $CALCULATE(...) expression
        if value.startswith("$CALCULATE("):
            result = self._evaluator.resolve_param_value(value)
            if result != value:  # Expression was evaluated
                return result
            # Fall through to try simple variable resolution

        # Check for $AUTO_* proportion parameters (TASK-041-14)
        if value.startswith("$AUTO_"):
            result = self._proportion_resolver.resolve(value)
            if result != value:  # Resolved successfully
                return result
            # Fall through if not resolved (no dimensions set)

        # Check for simple $variable reference
        if value.startswith("$") and not value.startswith("$CALCULATE") and not value.startswith("$AUTO_"):
            param_name = value[1:]
            if param_name in params:
                return params[param_name]
            # Try evaluator context (dimensions, etc.)
            result = self._evaluator.resolve_param_value(value)
            if result != value:
                return result
            return None  # Variable not found

        return value

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
