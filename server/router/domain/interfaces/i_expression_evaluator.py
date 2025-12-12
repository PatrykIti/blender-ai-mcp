"""
Expression Evaluator Interface.

TASK-060: Domain interface for expression evaluation.
Defines contract for safe expression evaluation used by workflow system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class IExpressionEvaluator(ABC):
    """Abstract interface for expression evaluation.

    Supports mathematical expressions, comparisons, and logical operations.
    All implementations must provide safe evaluation without arbitrary code execution.

    Implementations:
        - UnifiedEvaluator: Full AST-based implementation

    Example:
        evaluator: IExpressionEvaluator = UnifiedEvaluator()
        evaluator.set_context({"width": 2.0, "mode": "EDIT"})
        result = evaluator.evaluate("width > 1.0")  # -> 1.0
    """

    @abstractmethod
    def set_context(self, context: Dict[str, Any]) -> None:
        """Set variable context for evaluation.

        Args:
            context: Dictionary with variable values.
                     Supports: int, float, bool, str values.
        """
        pass

    @abstractmethod
    def get_context(self) -> Dict[str, Any]:
        """Get current evaluation context.

        Returns:
            Copy of current context dictionary.
        """
        pass

    @abstractmethod
    def update_context(self, updates: Dict[str, Any]) -> None:
        """Update context with new values (merge).

        Args:
            updates: Dictionary with values to add/update.
        """
        pass

    @abstractmethod
    def get_variable(self, name: str) -> Optional[Any]:
        """Get variable value from context.

        Args:
            name: Variable name.

        Returns:
            Variable value or None if not found.
        """
        pass

    @abstractmethod
    def evaluate(self, expression: str) -> Any:
        """Evaluate expression and return result.

        Args:
            expression: Expression string to evaluate.

        Returns:
            Evaluated value:
            - float for arithmetic expressions
            - float (1.0/0.0) for comparisons/logic (represents True/False)
            - str only in string literal contexts

        Raises:
            ValueError: If expression is invalid or uses disallowed constructs.
        """
        pass

    @abstractmethod
    def evaluate_safe(self, expression: str, default: Any = 0.0) -> Any:
        """Evaluate expression with fallback on error.

        Args:
            expression: Expression string to evaluate.
            default: Value to return on error.

        Returns:
            Evaluated value or default on error.
        """
        pass
