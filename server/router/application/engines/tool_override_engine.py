"""
Tool Override Engine Implementation.

Determines if a tool should be replaced with a better alternative.
"""

from typing import Dict, Any, Optional, List

from server.router.domain.interfaces.i_override_engine import IOverrideEngine
from server.router.domain.entities.scene_context import SceneContext
from server.router.domain.entities.pattern import DetectedPattern, PatternType
from server.router.domain.entities.override_decision import (
    OverrideDecision,
    OverrideReason,
    ReplacementTool,
)
from server.router.infrastructure.config import RouterConfig


class ToolOverrideEngine(IOverrideEngine):
    """Implementation of tool override decisions.

    Determines if a tool should be replaced with a better alternative
    or expanded into a workflow based on context and patterns.
    """

    def __init__(self, config: Optional[RouterConfig] = None):
        """Initialize override engine.

        Args:
            config: Router configuration (uses defaults if None).
        """
        self._config = config or RouterConfig()
        self._rules: Dict[str, Dict[str, Any]] = {}
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        """Register default override rules."""
        # Phone pattern: extrude → inset + extrude (screen cutout)
        self.register_rule(
            rule_name="extrude_for_screen",
            trigger_tool="mesh_extrude_region",
            trigger_pattern="phone_like",
            replacement_tools=[
                {
                    "tool_name": "mesh_inset",
                    "params": {"thickness": 0.03},
                    "description": "Inset for screen border",
                },
                {
                    "tool_name": "mesh_extrude_region",
                    "params": {"depth": -0.02},
                    "inherit_params": ["depth"],
                    "description": "Extrude inward for screen recess",
                },
            ],
        )

        # Tower pattern: subdivide → subdivide + select top + scale
        self.register_rule(
            rule_name="subdivide_tower",
            trigger_tool="mesh_subdivide",
            trigger_pattern="tower_like",
            replacement_tools=[
                {
                    "tool_name": "mesh_subdivide",
                    "params": {"number_cuts": 3},
                    "description": "Subdivide tower",
                },
                {
                    "tool_name": "mesh_select",
                    "params": {"action": "none"},
                    "description": "Deselect all",
                },
                {
                    "tool_name": "mesh_select_targeted",
                    "params": {"action": "by_location", "location": [0, 0, 1], "threshold": 0.1},
                    "description": "Select top vertices",
                },
                {
                    "tool_name": "mesh_transform_selected",
                    "params": {"scale": [0.7, 0.7, 1.0]},
                    "description": "Taper top",
                },
            ],
        )

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
        if not self._config.enable_overrides:
            return OverrideDecision.no_override()

        pattern_name = pattern.name if pattern else None

        # Check each rule
        for rule_name, rule in self._rules.items():
            if self._rule_matches(rule, tool_name, pattern_name):
                return self._create_override_decision(rule, params)

        return OverrideDecision.no_override()

    def _rule_matches(
        self,
        rule: Dict[str, Any],
        tool_name: str,
        pattern_name: Optional[str],
    ) -> bool:
        """Check if a rule matches the current context.

        Args:
            rule: Rule definition.
            tool_name: Tool being called.
            pattern_name: Detected pattern name.

        Returns:
            True if rule matches.
        """
        # Check tool match
        if rule["trigger_tool"] != tool_name:
            return False

        # Check pattern match if required
        if rule.get("trigger_pattern"):
            if pattern_name != rule["trigger_pattern"]:
                return False

        return True

    def _create_override_decision(
        self,
        rule: Dict[str, Any],
        original_params: Dict[str, Any],
    ) -> OverrideDecision:
        """Create override decision from rule.

        Args:
            rule: Matched rule definition.
            original_params: Original tool parameters.

        Returns:
            OverrideDecision with replacement tools.
        """
        replacement_tools = []
        for tool_def in rule["replacement_tools"]:
            replacement_tools.append(ReplacementTool(
                tool_name=tool_def["tool_name"],
                params=tool_def.get("params", {}),
                inherit_params=tool_def.get("inherit_params", []),
                description=tool_def.get("description", ""),
            ))

        reasons = [OverrideReason(
            rule_name=rule["rule_name"],
            description=f"Override triggered by rule: {rule['rule_name']}",
            pattern_match=rule.get("trigger_pattern"),
        )]

        return OverrideDecision.override_with_tools(replacement_tools, reasons)

    def get_override_rules(self) -> List[Dict[str, Any]]:
        """Get all registered override rules.

        Returns:
            List of override rule definitions.
        """
        return list(self._rules.values())

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
        self._rules[rule_name] = {
            "rule_name": rule_name,
            "trigger_tool": trigger_tool,
            "trigger_pattern": trigger_pattern,
            "replacement_tools": replacement_tools,
        }

    def remove_rule(self, rule_name: str) -> bool:
        """Remove an override rule.

        Args:
            rule_name: Name of the rule to remove.

        Returns:
            True if rule was removed, False if not found.
        """
        if rule_name in self._rules:
            del self._rules[rule_name]
            return True
        return False
