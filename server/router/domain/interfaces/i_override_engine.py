"""
Override Engine Interface.

Abstract interface for tool override decisions.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from server.router.domain.entities.scene_context import SceneContext
from server.router.domain.entities.pattern import DetectedPattern
from server.router.domain.entities.override_decision import OverrideDecision


class IOverrideEngine(ABC):
    """Abstract interface for tool override decisions.

    Determines if a tool should be replaced with a better alternative
    or expanded into a workflow.
    """

    @abstractmethod
    def check_override(
        self,
        tool_name: str,
        params: Dict[str, Any],
        context: SceneContext,
        pattern: Optional[DetectedPattern] = None,
    ) -> OverrideDecision:
        """Check if a tool should be overridden.

        Args:
            tool_name: Name of the tool to check.
            params: Original parameters.
            context: Current scene context.
            pattern: Detected geometry pattern (if any).

        Returns:
            OverrideDecision with replacement info.
        """
        pass

    @abstractmethod
    def get_override_rules(self) -> List[Dict[str, Any]]:
        """Get all registered override rules.

        Returns:
            List of override rule definitions.
        """
        pass

    @abstractmethod
    def register_rule(
        self,
        rule_name: str,
        trigger_tool: str,
        trigger_pattern: Optional[str],
        replacement_tools: List[Dict[str, Any]],
    ) -> None:
        """Register a new override rule.

        Args:
            rule_name: Unique name for the rule.
            trigger_tool: Tool that triggers this rule.
            trigger_pattern: Pattern that must match (optional).
            replacement_tools: List of replacement tool definitions.
        """
        pass

    @abstractmethod
    def remove_rule(self, rule_name: str) -> bool:
        """Remove an override rule.

        Args:
            rule_name: Name of the rule to remove.

        Returns:
            True if rule was removed, False if not found.
        """
        pass
