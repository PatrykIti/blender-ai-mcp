"""
Workflow Triggerer.

Automatically detects and triggers workflows based on:
1. Explicit goal set via router_set_goal (primary)
2. Heuristics based on tool + params + context (fallback)
3. Scene pattern detection (fallback)

TASK-041-0b
"""

import logging
from typing import Dict, Any, Optional, Callable, List

from server.router.domain.entities.scene_context import SceneContext
from server.router.domain.entities.pattern import DetectedPattern

logger = logging.getLogger(__name__)


# Type for heuristic function: (params, context) -> Optional[workflow_name]
HeuristicFunc = Callable[[Dict[str, Any], SceneContext], Optional[str]]


class WorkflowTriggerer:
    """Determines when to trigger workflows.

    Uses multiple sources to determine the appropriate workflow:
    1. Explicit goal (highest priority) - set via router_set_goal
    2. Keyword matching from goal
    3. Tool-based heuristics (fallback when no goal)
    4. Pattern-based detection (fallback)

    Attributes:
        _explicit_goal: Goal explicitly set by LLM.
        _explicit_workflow: Workflow matched from explicit goal.
    """

    # Tool-specific heuristics for guessing workflow
    # Format: {tool_name: {param_value: heuristic_func}}
    TOOL_HEURISTICS: Dict[str, Dict[str, HeuristicFunc]] = {}

    def __init__(self):
        """Initialize workflow triggerer."""
        self._explicit_goal: Optional[str] = None
        self._explicit_workflow: Optional[str] = None
        self._registry = None  # Lazy-loaded

        # Register default heuristics
        self._register_default_heuristics()

    def _get_registry(self):
        """Get or create the workflow registry.

        Returns:
            WorkflowRegistry instance.
        """
        if self._registry is None:
            from server.router.application.workflows.registry import get_workflow_registry
            self._registry = get_workflow_registry()
        return self._registry

    def _register_default_heuristics(self) -> None:
        """Register default tool heuristics."""
        # Heuristic: CUBE with flat Z scale → phone/tablet
        self.register_heuristic(
            tool_name="modeling_create_primitive",
            param_key="type",
            param_value="CUBE",
            heuristic=self._heuristic_flat_cube,
        )

        # Heuristic: CUBE with tall Z scale → tower
        self.register_heuristic(
            tool_name="modeling_transform_object",
            param_key="scale",
            param_value=None,  # Any scale value
            heuristic=self._heuristic_tall_scale,
        )

    def set_explicit_goal(self, goal: str) -> Optional[str]:
        """Set explicit modeling goal.

        Args:
            goal: User's modeling goal (e.g., "smartphone", "table")

        Returns:
            Matched workflow name or None.
        """
        self._explicit_goal = goal

        # Try to find matching workflow
        registry = self._get_registry()
        workflow_name = registry.find_by_keywords(goal)

        if workflow_name:
            self._explicit_workflow = workflow_name
            logger.info(f"[TRIGGERER] Goal '{goal}' matched workflow: {workflow_name}")
        else:
            self._explicit_workflow = None
            logger.info(f"[TRIGGERER] Goal '{goal}' set (no matching workflow)")

        return workflow_name

    def get_explicit_goal(self) -> Optional[str]:
        """Get current explicit goal."""
        return self._explicit_goal

    def get_explicit_workflow(self) -> Optional[str]:
        """Get workflow matched from explicit goal."""
        return self._explicit_workflow

    def clear_goal(self) -> None:
        """Clear current goal."""
        self._explicit_goal = None
        self._explicit_workflow = None
        logger.info("[TRIGGERER] Goal cleared")

    def determine_workflow(
        self,
        tool_name: str,
        params: Dict[str, Any],
        context: SceneContext,
        pattern: Optional[DetectedPattern] = None,
    ) -> Optional[str]:
        """Determine appropriate workflow for tool call.

        Priority:
        1. Explicit workflow (from router_set_goal)
        2. Pattern-suggested workflow
        3. Heuristic-based detection

        Args:
            tool_name: Name of tool being called.
            params: Tool parameters.
            context: Current scene context.
            pattern: Detected pattern (if any).

        Returns:
            Workflow name or None.
        """
        # Priority 1: Explicit workflow from goal
        if self._explicit_workflow:
            logger.debug(f"[TRIGGERER] Using explicit workflow: {self._explicit_workflow}")
            return self._explicit_workflow

        # Priority 2: Pattern-suggested workflow
        if pattern and pattern.suggested_workflow:
            logger.debug(f"[TRIGGERER] Using pattern workflow: {pattern.suggested_workflow}")
            return pattern.suggested_workflow

        # Priority 3: Heuristic-based detection
        heuristic_workflow = self._check_heuristic_trigger(tool_name, params, context)
        if heuristic_workflow:
            logger.info(f"[TRIGGERER] Heuristic detected workflow: {heuristic_workflow}")
            return heuristic_workflow

        return None

    def register_heuristic(
        self,
        tool_name: str,
        param_key: str,
        param_value: Any,
        heuristic: HeuristicFunc,
    ) -> None:
        """Register a heuristic for workflow detection.

        Args:
            tool_name: Tool name to match.
            param_key: Parameter key to check.
            param_value: Parameter value to match (None for any).
            heuristic: Function that returns workflow name or None.
        """
        if tool_name not in self.TOOL_HEURISTICS:
            self.TOOL_HEURISTICS[tool_name] = {}

        key = f"{param_key}:{param_value}" if param_value else param_key
        self.TOOL_HEURISTICS[tool_name][key] = heuristic

    def _check_heuristic_trigger(
        self,
        tool_name: str,
        params: Dict[str, Any],
        context: SceneContext,
    ) -> Optional[str]:
        """Guess workflow based on tool + params + context.

        Args:
            tool_name: Tool being called.
            params: Tool parameters.
            context: Scene context.

        Returns:
            Workflow name or None.
        """
        if tool_name not in self.TOOL_HEURISTICS:
            return None

        tool_heuristics = self.TOOL_HEURISTICS[tool_name]

        for key, heuristic in tool_heuristics.items():
            # Parse the key
            if ":" in key:
                param_key, param_value = key.split(":", 1)
                # Check if param matches
                if params.get(param_key) != param_value:
                    continue
            else:
                param_key = key
                if param_key not in params:
                    continue

            # Run heuristic
            result = heuristic(params, context)
            if result:
                return result

        return None

    # --- Default Heuristics ---

    def _heuristic_flat_cube(
        self,
        params: Dict[str, Any],
        context: SceneContext,
    ) -> Optional[str]:
        """Detect phone/tablet from flat cube creation.

        If creating a CUBE and context suggests flat object,
        might be a phone/tablet workflow.
        """
        # Check if we're at the start (no complex context yet)
        if context.proportions and context.proportions.is_flat:
            # Existing flat object → might be phone
            return "phone_workflow"

        # Can't determine yet
        return None

    def _heuristic_tall_scale(
        self,
        params: Dict[str, Any],
        context: SceneContext,
    ) -> Optional[str]:
        """Detect tower from tall scale transformation.

        If scaling with tall Z ratio, might be a tower.
        """
        scale = params.get("scale")
        if not scale or not isinstance(scale, (list, tuple)):
            return None

        if len(scale) < 3:
            return None

        x, y, z = scale[0], scale[1], scale[2]

        # Check if Z is significantly taller than X and Y
        if z > 3 * max(x, y):
            return "tower_workflow"

        # Check if flat (phone-like)
        if z < 0.2 * min(x, y):
            return "phone_workflow"

        return None

    def get_available_workflows(self) -> List[str]:
        """Get list of available workflows.

        Returns:
            List of workflow names.
        """
        registry = self._get_registry()
        return registry.get_all_workflows()
