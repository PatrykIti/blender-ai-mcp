"""
Error Firewall Implementation.

Validates and blocks/fixes invalid operations before execution.
"""

from typing import Dict, Any, List, Optional
import re

from server.router.domain.interfaces.i_firewall import IFirewall
from server.router.domain.entities.tool_call import CorrectedToolCall
from server.router.domain.entities.scene_context import SceneContext
from server.router.domain.entities.firewall_result import (
    FirewallResult,
    FirewallAction,
    FirewallViolation,
    FirewallRuleType,
)
from server.router.infrastructure.config import RouterConfig


class ErrorFirewall(IFirewall):
    """Implementation of operation validation.

    Validates tool calls and blocks or fixes invalid operations.
    """

    def __init__(self, config: Optional[RouterConfig] = None):
        """Initialize firewall.

        Args:
            config: Router configuration (uses defaults if None).
        """
        self._config = config or RouterConfig()
        self._rules: Dict[str, Dict[str, Any]] = {}
        self._disabled_rules: set = set()
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        """Register default firewall rules."""
        # Mode violation rules
        self.register_rule(
            rule_name="mesh_in_object_mode",
            tool_pattern="mesh_*",
            condition="mode == 'OBJECT'",
            action="auto_fix",
            fix_description="Switch to EDIT mode",
        )

        self.register_rule(
            rule_name="modeling_in_edit_mode",
            tool_pattern="modeling_*",
            condition="mode == 'EDIT'",
            action="auto_fix",
            fix_description="Switch to OBJECT mode",
        )

        self.register_rule(
            rule_name="sculpt_in_wrong_mode",
            tool_pattern="sculpt_*",
            condition="mode != 'SCULPT'",
            action="auto_fix",
            fix_description="Switch to SCULPT mode",
        )

        # Selection rules
        self.register_rule(
            rule_name="extrude_no_selection",
            tool_pattern="mesh_extrude_region",
            condition="no_selection",
            action="auto_fix",
            fix_description="Select all geometry",
        )

        self.register_rule(
            rule_name="bevel_no_selection",
            tool_pattern="mesh_bevel",
            condition="no_selection",
            action="auto_fix",
            fix_description="Select all geometry",
        )

        # Parameter rules
        self.register_rule(
            rule_name="bevel_too_large",
            tool_pattern="mesh_bevel",
            condition="param:offset > dimension_ratio:0.5",
            action="modify",
            fix_description="Clamp bevel offset",
        )

        self.register_rule(
            rule_name="subdivide_too_many",
            tool_pattern="mesh_subdivide",
            condition="param:number_cuts > 6",
            action="modify",
            fix_description="Limit subdivision cuts",
        )

        # Object existence rules
        self.register_rule(
            rule_name="delete_no_object",
            tool_pattern="scene_delete_object",
            condition="no_objects",
            action="block",
            fix_description="",
        )

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
        violations = []
        pre_steps = []
        modified_params = None

        # Check each rule
        for rule_name, rule in self._rules.items():
            if rule_name in self._disabled_rules:
                continue

            if self._rule_matches(rule, tool_call, context):
                violation = self._create_violation(rule, tool_call, context)
                violations.append(violation)

                if rule["action"] == "block":
                    return FirewallResult.block(
                        f"Blocked by rule: {rule_name}",
                        violations,
                    )

                elif rule["action"] == "auto_fix" and self._config.auto_fix_mode_violations:
                    fix_result = self._apply_auto_fix(rule, tool_call, context)
                    if fix_result:
                        pre_steps.extend(fix_result.get("pre_steps", []))
                        if fix_result.get("modified_params"):
                            modified_params = fix_result["modified_params"]

                elif rule["action"] == "modify":
                    modified = self._apply_modification(rule, tool_call, context)
                    if modified:
                        modified_params = modified

        # Return result based on violations
        if violations:
            if pre_steps or modified_params:
                modified_call = None
                if modified_params:
                    modified_call = {
                        "tool": tool_call.tool_name,
                        "params": modified_params,
                    }
                return FirewallResult.auto_fix(
                    f"Auto-fixed {len(violations)} issue(s)",
                    modified_call=modified_call,
                    pre_steps=pre_steps,
                    violations=violations,
                )

        return FirewallResult.allow()

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
        results = []
        current_context = context

        for call in calls:
            result = self.validate(call, current_context)
            results.append(result)

            # Update simulated context based on call
            # (simplified - in practice would need full simulation)

        return results

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
        for rule_name, rule in self._rules.items():
            if rule_name in self._disabled_rules:
                continue

            if self._rule_matches(rule, tool_call, context):
                if rule["action"] in ("auto_fix", "modify"):
                    return True
                if rule["action"] == "block":
                    return False

        return True

    def get_firewall_rules(self) -> List[Dict[str, Any]]:
        """Get all registered firewall rules.

        Returns:
            List of firewall rule definitions.
        """
        return [
            {**rule, "enabled": rule["rule_name"] not in self._disabled_rules}
            for rule in self._rules.values()
        ]

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
        self._rules[rule_name] = {
            "rule_name": rule_name,
            "tool_pattern": tool_pattern,
            "condition": condition,
            "action": action,
            "fix_description": fix_description,
        }

    def enable_rule(self, rule_name: str) -> bool:
        """Enable a firewall rule.

        Args:
            rule_name: Name of rule to enable.

        Returns:
            True if rule was found and enabled.
        """
        if rule_name in self._rules:
            self._disabled_rules.discard(rule_name)
            return True
        return False

    def disable_rule(self, rule_name: str) -> bool:
        """Disable a firewall rule.

        Args:
            rule_name: Name of rule to disable.

        Returns:
            True if rule was found and disabled.
        """
        if rule_name in self._rules:
            self._disabled_rules.add(rule_name)
            return True
        return False

    def _rule_matches(
        self,
        rule: Dict[str, Any],
        tool_call: CorrectedToolCall,
        context: SceneContext,
    ) -> bool:
        """Check if a rule matches the tool call and context.

        Args:
            rule: Rule definition.
            tool_call: Tool call to check.
            context: Current scene context.

        Returns:
            True if rule matches.
        """
        # Check tool pattern
        pattern = rule["tool_pattern"]
        if not self._matches_pattern(pattern, tool_call.tool_name):
            return False

        # Check condition
        condition = rule["condition"]
        return self._evaluate_condition(condition, tool_call, context)

    def _matches_pattern(self, pattern: str, tool_name: str) -> bool:
        """Check if tool name matches pattern.

        Args:
            pattern: Pattern with optional wildcards.
            tool_name: Tool name to match.

        Returns:
            True if matches.
        """
        if pattern == tool_name:
            return True

        # Convert glob pattern to regex
        regex = pattern.replace("*", ".*")
        return bool(re.match(f"^{regex}$", tool_name))

    def _evaluate_condition(
        self,
        condition: str,
        tool_call: CorrectedToolCall,
        context: SceneContext,
    ) -> bool:
        """Evaluate a condition expression.

        Args:
            condition: Condition string.
            tool_call: Tool call for param access.
            context: Scene context.

        Returns:
            True if condition is met.
        """
        # Simple condition parser
        if condition.startswith("mode == "):
            mode = condition.split("'")[1]
            return context.mode == mode

        if condition.startswith("mode != "):
            mode = condition.split("'")[1]
            return context.mode != mode

        if condition == "no_selection":
            return not context.has_selection

        if condition == "no_objects":
            return len(context.objects) == 0

        if condition.startswith("param:"):
            # param:offset > dimension_ratio:0.5
            parts = condition.split()
            if len(parts) >= 3:
                param_part = parts[0].replace("param:", "")
                operator = parts[1]
                value_part = parts[2]

                param_value = tool_call.params.get(param_part)
                if param_value is None:
                    return False

                if value_part.startswith("dimension_ratio:"):
                    ratio = float(value_part.split(":")[1])
                    dims = context.get_active_dimensions()
                    if dims:
                        max_allowed = min(dims) * ratio
                        if operator == ">":
                            return param_value > max_allowed

                else:
                    compare_value = float(value_part)
                    if operator == ">":
                        return param_value > compare_value
                    elif operator == "<":
                        return param_value < compare_value

        return False

    def _create_violation(
        self,
        rule: Dict[str, Any],
        tool_call: CorrectedToolCall,
        context: SceneContext,
    ) -> FirewallViolation:
        """Create a violation object for a matched rule.

        Args:
            rule: Matched rule.
            tool_call: Tool call that violated.
            context: Scene context.

        Returns:
            FirewallViolation object.
        """
        rule_type = self._get_rule_type(rule)

        return FirewallViolation(
            rule_type=rule_type,
            message=f"Rule '{rule['rule_name']}' triggered: {rule['condition']}",
            severity="warning" if rule["action"] in ("auto_fix", "modify") else "error",
            can_auto_fix=rule["action"] in ("auto_fix", "modify"),
            fix_description=rule.get("fix_description"),
        )

    def _get_rule_type(self, rule: Dict[str, Any]) -> FirewallRuleType:
        """Determine rule type from rule definition.

        Args:
            rule: Rule definition.

        Returns:
            FirewallRuleType enum value.
        """
        condition = rule["condition"]

        if "mode" in condition:
            return FirewallRuleType.MODE_VIOLATION
        if "selection" in condition:
            return FirewallRuleType.SELECTION_REQUIRED
        if "param:" in condition:
            return FirewallRuleType.PARAMETER_OUT_OF_RANGE
        if "no_objects" in condition:
            return FirewallRuleType.OBJECT_NOT_FOUND

        return FirewallRuleType.INVALID_OPERATION

    def _apply_auto_fix(
        self,
        rule: Dict[str, Any],
        tool_call: CorrectedToolCall,
        context: SceneContext,
    ) -> Optional[Dict[str, Any]]:
        """Apply auto-fix for a rule violation.

        Args:
            rule: Matched rule.
            tool_call: Tool call to fix.
            context: Scene context.

        Returns:
            Dict with pre_steps and/or modified_params, or None.
        """
        condition = rule["condition"]
        result: Dict[str, Any] = {"pre_steps": []}

        # Mode fixes
        if "mode ==" in condition or "mode !=" in condition:
            target_mode = self._get_required_mode_for_tool(tool_call.tool_name)
            if target_mode and target_mode != context.mode:
                result["pre_steps"].append({
                    "tool": "system_set_mode",
                    "params": {"mode": target_mode},
                })

        # Selection fixes
        if condition == "no_selection":
            result["pre_steps"].append({
                "tool": "mesh_select",
                "params": {"action": "all"},
            })

        return result if result["pre_steps"] else None

    def _apply_modification(
        self,
        rule: Dict[str, Any],
        tool_call: CorrectedToolCall,
        context: SceneContext,
    ) -> Optional[Dict[str, Any]]:
        """Apply parameter modification for a rule.

        Args:
            rule: Matched rule.
            tool_call: Tool call to modify.
            context: Scene context.

        Returns:
            Modified parameters dict, or None.
        """
        condition = rule["condition"]
        modified = dict(tool_call.params)

        if "param:" in condition and "dimension_ratio" in condition:
            # Extract param name and ratio
            parts = condition.split()
            param_name = parts[0].replace("param:", "")
            ratio = float(parts[2].split(":")[1])

            dims = context.get_active_dimensions()
            if dims and param_name in modified:
                max_allowed = min(dims) * ratio
                modified[param_name] = min(modified[param_name], max_allowed)

        elif "param:" in condition:
            # param:number_cuts > 6
            parts = condition.split()
            param_name = parts[0].replace("param:", "")
            max_value = float(parts[2])

            if param_name in modified:
                modified[param_name] = min(modified[param_name], int(max_value))

        return modified

    def _get_required_mode_for_tool(self, tool_name: str) -> Optional[str]:
        """Get required mode for a tool.

        Args:
            tool_name: Tool name.

        Returns:
            Required mode or None.
        """
        if tool_name.startswith("mesh_"):
            return "EDIT"
        if tool_name.startswith("modeling_"):
            return "OBJECT"
        if tool_name.startswith("sculpt_"):
            return "SCULPT"
        return None
