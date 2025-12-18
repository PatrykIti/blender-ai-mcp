"""
Condition Evaluator.

Evaluates boolean conditions for workflow step execution.
Supports comparisons, boolean variables, and logical operators.

TASK-041-10: Original implementation
TASK-060: Refactored to delegate to UnifiedEvaluator.
"""

import logging
from typing import Dict, Any

from server.router.application.evaluator.unified_evaluator import UnifiedEvaluator

logger = logging.getLogger(__name__)


class ConditionEvaluator:
    """Evaluates boolean conditions for workflow step execution.

    This is a wrapper around UnifiedEvaluator that provides:
    - Boolean return type (converts result to bool)
    - Fail-open behavior (returns True on error)
    - Step effect simulation (simulate_step_effect)
    - SceneContext adapter (set_context_from_scene)

    TASK-060: Now delegates evaluation to UnifiedEvaluator.
    NEW capabilities:
    - Math functions in conditions: "floor(width) > 5"
    - Ternary expressions: "1 if has_selection else 0"

    Supported conditions:
    - "current_mode != 'EDIT'"
    - "has_selection"
    - "not has_selection"
    - "object_count > 0"
    - "width > 1.0 and height < 2.0"
    - "floor(table_width / plank_width) > 5"  # NEW in TASK-060

    Supported operators:
    - Comparison: ==, !=, >, <, >=, <=
    - Logical: not (prefix), and, or
    - Grouping: parentheses () with proper precedence (TASK-056-2)

    Operator precedence (highest to lowest):
    1. Parentheses ()
    2. not
    3. and
    4. or

    Example:
        evaluator = ConditionEvaluator()
        evaluator.set_context({"current_mode": "OBJECT", "has_selection": False})
        evaluator.evaluate("current_mode != 'EDIT'")  # -> True
        evaluator.evaluate("has_selection")  # -> False
        evaluator.evaluate("not has_selection")  # -> True
        evaluator.evaluate("(A and B) or (C and D)")  # -> with parentheses (TASK-056-2)
        evaluator.evaluate("not (A or B)")  # -> negation with grouping (TASK-056-2)
    """

    def __init__(self):
        """Initialize condition evaluator."""
        self._unified = UnifiedEvaluator()

    def set_context(self, context: Dict[str, Any]) -> None:
        """Set evaluation context.

        Args:
            context: Dictionary with variable values.

        Expected keys:
        - current_mode: str (e.g., "OBJECT", "EDIT", "SCULPT")
        - has_selection: bool
        - object_count: int
        - active_object: str (object name)
        - selected_verts, selected_edges, selected_faces: int
        """
        self._unified.set_context(context)

    def set_context_from_scene(self, scene_context: Any) -> None:
        """Set context from SceneContext object.

        Args:
            scene_context: SceneContext instance.
        """
        context: Dict[str, Any] = {
            "current_mode": scene_context.mode,
            "has_selection": scene_context.has_selection,
            "object_count": len(scene_context.objects) if scene_context.objects else 0,
            "active_object": scene_context.active_object,
        }

        if scene_context.topology:
            context["selected_verts"] = scene_context.topology.selected_verts
            context["selected_edges"] = scene_context.topology.selected_edges
            context["selected_faces"] = scene_context.topology.selected_faces
            context["total_verts"] = scene_context.topology.total_verts
            context["total_edges"] = scene_context.topology.total_edges
            context["total_faces"] = scene_context.topology.total_faces

        self._unified.set_context(context)

    def get_context(self) -> Dict[str, Any]:
        """Get current evaluation context.

        Returns:
            Copy of current context dictionary.
        """
        return self._unified.get_context()

    def update_context(self, updates: Dict[str, Any]) -> None:
        """Update context with new values.

        Args:
            updates: Dictionary with values to update.
        """
        self._unified.update_context(updates)

    def evaluate(self, condition: str) -> bool:
        """Evaluate a condition string.

        Args:
            condition: Condition expression.

        Returns:
            True if condition is met, False otherwise.
            Returns True if condition is empty or invalid (fail-open).
        """
        if not condition or not condition.strip():
            return True

        condition = condition.strip()

        try:
            logger.debug(
                f"Evaluating condition '{condition}' with context keys: "
                f"{list(self._unified.get_context().keys())}"
            )
            result = self._unified.evaluate_as_bool(condition)
            logger.debug(f"Condition '{condition}' evaluated to {result}")
            return result
        except Exception as e:
            logger.warning(f"Condition evaluation failed: '{condition}' - {e}")
            return True  # Fail-open: execute step if condition can't be evaluated

    def simulate_step_effect(self, tool_name: str, params: Dict[str, Any]) -> None:
        """Simulate the effect of a workflow step on context.

        Updates the context to reflect what would happen after
        executing a tool. Used for conditional step evaluation
        within a workflow.

        NOTE: This method is NOT delegated to UnifiedEvaluator because
        it's workflow-specific logic, not expression evaluation logic.

        Args:
            tool_name: Name of the tool being executed.
            params: Tool parameters.
        """
        updates: Dict[str, Any] = {}

        if tool_name == "system_set_mode":
            mode = params.get("mode")
            if mode:
                updates["current_mode"] = mode

        elif tool_name == "scene_set_mode":
            mode = params.get("mode")
            if mode:
                updates["current_mode"] = mode

        elif tool_name == "mesh_select":
            action = params.get("action")
            if action == "all":
                updates["has_selection"] = True
            elif action == "none":
                updates["has_selection"] = False

        elif tool_name == "mesh_select_targeted":
            # Targeted selection typically results in some selection
            updates["has_selection"] = True

        elif tool_name == "modeling_create_primitive":
            # Creating an object increases object count
            current_count = self._unified.get_context().get("object_count", 0)
            updates["object_count"] = current_count + 1

        elif tool_name == "scene_delete_object":
            # Deleting an object decreases object count
            current_count = self._unified.get_context().get("object_count", 0)
            if current_count > 0:
                updates["object_count"] = current_count - 1

        if updates:
            self._unified.update_context(updates)
