"""
Workflow Expansion Engine Implementation.

Transforms single tool calls into multi-step workflows.
Supports parametric variable substitution (TASK-052).
"""

import logging
from typing import Dict, Any, Optional, List, Union

from server.router.domain.interfaces.i_expansion_engine import IExpansionEngine
from server.router.domain.entities.tool_call import CorrectedToolCall
from server.router.domain.entities.scene_context import SceneContext
from server.router.domain.entities.pattern import DetectedPattern
from server.router.infrastructure.config import RouterConfig

logger = logging.getLogger(__name__)


def extract_modifiers(
    prompt: str, workflow_modifiers: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """Extract variable overrides from user prompt based on workflow modifiers.

    Scans the user prompt for keywords defined in workflow modifiers and
    returns the corresponding variable overrides.

    Args:
        prompt: User prompt to scan for keywords.
        workflow_modifiers: Dictionary mapping keywords to variable overrides.
            Example: {"straight legs": {"leg_angle": 0}}

    Returns:
        Dictionary of variable overrides found in the prompt.
        Later matches override earlier ones.

    Example:
        >>> modifiers = {"straight legs": {"angle": 0}, "angled": {"angle": 0.32}}
        >>> extract_modifiers("table with straight legs", modifiers)
        {"angle": 0}
    """
    overrides: Dict[str, Any] = {}
    prompt_lower = prompt.lower()

    for keyword, values in workflow_modifiers.items():
        if keyword.lower() in prompt_lower:
            overrides.update(values)
            logger.debug(f"Modifier matched: '{keyword}' → {values}")

    return overrides


def substitute_variables(
    params: Dict[str, Any], variables: Dict[str, Any]
) -> Dict[str, Any]:
    """Replace $variable placeholders with actual values.

    Handles both top-level string values and values within lists.
    Variables are referenced with $ prefix (e.g., "$leg_angle").

    Args:
        params: Parameters dictionary with potential $variable references.
        variables: Dictionary of variable names to values.

    Returns:
        New parameters dictionary with variables substituted.

    Example:
        >>> params = {"rotation": [0, "$angle", 0], "name": "Leg"}
        >>> variables = {"angle": 0.32}
        >>> substitute_variables(params, variables)
        {"rotation": [0, 0.32, 0], "name": "Leg"}
    """
    result: Dict[str, Any] = {}

    for key, value in params.items():
        if isinstance(value, str) and value.startswith("$"):
            # Direct $variable reference
            var_name = value[1:]  # Remove $
            if var_name in variables:
                result[key] = variables[var_name]
                logger.debug(f"Substituted ${var_name} → {variables[var_name]}")
            else:
                # Keep as-is if variable not found (might be $CALCULATE etc.)
                result[key] = value
        elif isinstance(value, list):
            # Check list elements for $variable references
            result[key] = _substitute_list(value, variables)
        elif isinstance(value, dict):
            # Recursively handle nested dicts
            result[key] = substitute_variables(value, variables)
        else:
            result[key] = value

    return result


def _substitute_list(lst: List[Any], variables: Dict[str, Any]) -> List[Any]:
    """Substitute variables in list elements.

    Args:
        lst: List with potential $variable references.
        variables: Dictionary of variable names to values.

    Returns:
        New list with variables substituted.
    """
    result = []
    for item in lst:
        if isinstance(item, str) and item.startswith("$"):
            var_name = item[1:]
            if var_name in variables:
                result.append(variables[var_name])
            else:
                result.append(item)
        elif isinstance(item, list):
            result.append(_substitute_list(item, variables))
        elif isinstance(item, dict):
            result.append(substitute_variables(item, variables))
        else:
            result.append(item)
    return result


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
        user_prompt: Optional[str] = None,
    ) -> List[CorrectedToolCall]:
        """Expand a named workflow with parameters.

        Args:
            workflow_name: Name of the workflow to expand.
            params: Parameters to pass to workflow steps.
            user_prompt: Optional user prompt for modifier extraction (TASK-052).

        Returns:
            List of expanded tool calls.
        """
        registry = self._get_registry()

        # Use registry's expand_workflow which handles both built-in and custom
        # Pass user_prompt for TASK-052 modifier extraction
        calls = registry.expand_workflow(workflow_name, params, user_prompt=user_prompt)

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
