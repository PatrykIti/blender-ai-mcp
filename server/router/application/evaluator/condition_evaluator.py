"""
Condition Evaluator.

Evaluates boolean conditions for workflow step execution.
Supports comparisons, boolean variables, and logical operators.

TASK-041-10
"""

import re
import logging
from typing import Dict, Any, Optional, Union

logger = logging.getLogger(__name__)


class ConditionEvaluator:
    """Evaluates boolean conditions for workflow step execution.

    Supported conditions:
    - "current_mode != 'EDIT'"
    - "has_selection"
    - "not has_selection"
    - "object_count > 0"
    - "active_object == 'Cube'"
    - "selected_verts >= 4"

    Supported operators:
    - Comparison: ==, !=, >, <, >=, <=
    - Logical: not (prefix), and, or

    Example:
        evaluator = ConditionEvaluator()
        evaluator.set_context({"current_mode": "OBJECT", "has_selection": False})
        evaluator.evaluate("current_mode != 'EDIT'")  # -> True
        evaluator.evaluate("has_selection")  # -> False
        evaluator.evaluate("not has_selection")  # -> True
    """

    # Comparison operators (order matters - check >= before >)
    COMPARISONS = [
        (">=", lambda a, b: a >= b),
        ("<=", lambda a, b: a <= b),
        ("!=", lambda a, b: a != b),
        ("==", lambda a, b: a == b),
        (">", lambda a, b: a > b),
        ("<", lambda a, b: a < b),
    ]

    def __init__(self):
        """Initialize condition evaluator."""
        self._context: Dict[str, Any] = {}

    def set_context(self, context: Dict[str, Any]) -> None:
        """Set evaluation context.

        Args:
            context: Dictionary with variable values.

        Expected keys:
        - current_mode: str (e.g., "OBJECT", "EDIT", "SCULPT")
        - has_selection: bool
        - object_count: int
        - active_object: str (object name)
        - selected_verts: int
        - selected_edges: int
        - selected_faces: int
        """
        self._context = dict(context) if context else {}

    def set_context_from_scene(self, scene_context: Any) -> None:
        """Set context from SceneContext object.

        Args:
            scene_context: SceneContext instance.
        """
        self._context = {
            "current_mode": scene_context.mode,
            "has_selection": scene_context.has_selection,
            "object_count": len(scene_context.objects) if scene_context.objects else 0,
            "active_object": scene_context.active_object,
        }

        if scene_context.topology:
            self._context["selected_verts"] = scene_context.topology.selected_verts
            self._context["selected_edges"] = scene_context.topology.selected_edges
            self._context["selected_faces"] = scene_context.topology.selected_faces
            self._context["total_verts"] = scene_context.topology.total_verts
            self._context["total_edges"] = scene_context.topology.total_edges
            self._context["total_faces"] = scene_context.topology.total_faces

    def get_context(self) -> Dict[str, Any]:
        """Get current evaluation context.

        Returns:
            Copy of current context dictionary.
        """
        return dict(self._context)

    def update_context(self, updates: Dict[str, Any]) -> None:
        """Update context with new values.

        Args:
            updates: Dictionary with values to update.
        """
        self._context.update(updates)

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
            result = self._evaluate_expression(condition)
            logger.debug(f"Condition '{condition}' evaluated to {result}")
            return result
        except Exception as e:
            logger.warning(f"Condition evaluation failed: '{condition}' - {e}")
            return True  # Fail-open: execute step if condition can't be evaluated

    def _evaluate_expression(self, condition: str) -> bool:
        """Evaluate a condition expression.

        Args:
            condition: Condition string.

        Returns:
            Boolean result.
        """
        condition = condition.strip()

        # Handle "not X" prefix
        if condition.startswith("not "):
            inner = condition[4:].strip()
            return not self._evaluate_expression(inner)

        # Handle "X and Y"
        if " and " in condition:
            parts = condition.split(" and ", 1)
            left = self._evaluate_expression(parts[0].strip())
            right = self._evaluate_expression(parts[1].strip())
            return left and right

        # Handle "X or Y"
        if " or " in condition:
            parts = condition.split(" or ", 1)
            left = self._evaluate_expression(parts[0].strip())
            right = self._evaluate_expression(parts[1].strip())
            return left or right

        # Handle comparisons
        for op, func in self.COMPARISONS:
            if op in condition:
                parts = condition.split(op, 1)
                if len(parts) == 2:
                    left = self._resolve_value(parts[0].strip())
                    right = self._resolve_value(parts[1].strip())
                    return func(left, right)

        # Handle boolean variables directly
        if condition in self._context:
            return bool(self._context[condition])

        # Handle boolean literals
        if condition.lower() == "true":
            return True
        if condition.lower() == "false":
            return False

        logger.warning(f"Could not parse condition: {condition}")
        return True  # Fail-open

    def _resolve_value(self, value_str: str) -> Any:
        """Resolve a value from string representation.

        Args:
            value_str: String representation of value.

        Returns:
            Resolved value (string, number, bool, or context variable).
        """
        value_str = value_str.strip()

        # String literal (single or double quotes)
        if (value_str.startswith("'") and value_str.endswith("'")) or \
           (value_str.startswith('"') and value_str.endswith('"')):
            return value_str[1:-1]

        # Boolean literals
        if value_str.lower() == "true":
            return True
        if value_str.lower() == "false":
            return False

        # None/null
        if value_str.lower() in ("none", "null"):
            return None

        # Number (try int first, then float)
        try:
            if "." in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass

        # Variable reference from context
        if value_str in self._context:
            return self._context[value_str]

        # Return as-is (unknown variable)
        logger.debug(f"Unknown variable in condition: {value_str}")
        return value_str

    def simulate_step_effect(self, tool_name: str, params: Dict[str, Any]) -> None:
        """Simulate the effect of a workflow step on context.

        Updates the context to reflect what would happen after
        executing a tool. Used for conditional step evaluation
        within a workflow.

        Args:
            tool_name: Name of the tool being executed.
            params: Tool parameters.
        """
        if tool_name == "system_set_mode":
            mode = params.get("mode")
            if mode:
                self._context["current_mode"] = mode

        elif tool_name == "scene_set_mode":
            mode = params.get("mode")
            if mode:
                self._context["current_mode"] = mode

        elif tool_name == "mesh_select":
            action = params.get("action")
            if action == "all":
                self._context["has_selection"] = True
            elif action == "none":
                self._context["has_selection"] = False

        elif tool_name == "mesh_select_targeted":
            # Targeted selection typically results in some selection
            self._context["has_selection"] = True

        elif tool_name == "modeling_create_primitive":
            # Creating an object increases object count
            current_count = self._context.get("object_count", 0)
            self._context["object_count"] = current_count + 1

        elif tool_name == "scene_delete_object":
            # Deleting an object decreases object count
            current_count = self._context.get("object_count", 0)
            if current_count > 0:
                self._context["object_count"] = current_count - 1
