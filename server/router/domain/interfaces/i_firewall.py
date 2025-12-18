"""
Error Firewall Interface.

Abstract interface for validating and blocking invalid operations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List

from server.router.domain.entities.tool_call import CorrectedToolCall
from server.router.domain.entities.scene_context import SceneContext
from server.router.domain.entities.firewall_result import FirewallResult


class IFirewall(ABC):
    """Abstract interface for operation validation.

    Validates tool calls and blocks or fixes invalid operations.
    """

    @abstractmethod
    def validate(
        self,
        tool_call: CorrectedToolCall,
        context: SceneContext,
    ) -> FirewallResult:
        """Validate a tool call against firewall rules.

        Args:
            tool_call: Tool call to validate.
            context: Current scene context.

        Returns:
            FirewallResult with validation outcome.
        """
        pass

    @abstractmethod
    def validate_sequence(
        self,
        calls: List[CorrectedToolCall],
        context: SceneContext,
    ) -> List[FirewallResult]:
        """Validate a sequence of tool calls.

        Args:
            calls: List of tool calls to validate.
            context: Current scene context.

        Returns:
            List of FirewallResult for each call.
        """
        pass

    @abstractmethod
    def can_auto_fix(
        self,
        tool_call: CorrectedToolCall,
        context: SceneContext,
    ) -> bool:
        """Check if a tool call can be auto-fixed.

        Args:
            tool_call: Tool call to check.
            context: Current scene context.

        Returns:
            True if auto-fix is possible.
        """
        pass

    @abstractmethod
    def get_firewall_rules(self) -> List[Dict[str, Any]]:
        """Get all registered firewall rules.

        Returns:
            List of firewall rule definitions.
        """
        pass

    @abstractmethod
    def register_rule(
        self,
        rule_name: str,
        tool_pattern: str,
        condition: str,
        action: str,
        fix_description: str = "",
    ) -> None:
        """Register a new firewall rule.

        Args:
            rule_name: Unique name for the rule.
            tool_pattern: Tool name pattern to match.
            condition: Condition expression.
            action: Action to take (allow, block, modify, auto_fix).
            fix_description: Description of auto-fix (if applicable).
        """
        pass

    @abstractmethod
    def enable_rule(self, rule_name: str) -> bool:
        """Enable a firewall rule.

        Args:
            rule_name: Name of rule to enable.

        Returns:
            True if rule was found and enabled.
        """
        pass

    @abstractmethod
    def disable_rule(self, rule_name: str) -> bool:
        """Disable a firewall rule.

        Args:
            rule_name: Name of rule to disable.

        Returns:
            True if rule was found and disabled.
        """
        pass
