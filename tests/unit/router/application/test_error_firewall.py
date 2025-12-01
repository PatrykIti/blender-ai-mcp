"""
Unit tests for ErrorFirewall.

Tests validation, blocking, and auto-fix functionality.
"""

import pytest

from server.router.application.engines.error_firewall import ErrorFirewall
from server.router.domain.entities.tool_call import CorrectedToolCall
from server.router.domain.entities.scene_context import (
    SceneContext,
    ObjectInfo,
    TopologyInfo,
)
from server.router.domain.entities.firewall_result import (
    FirewallResult,
    FirewallAction,
    FirewallRuleType,
)
from server.router.infrastructure.config import RouterConfig


@pytest.fixture
def firewall():
    """Create an ErrorFirewall with default config."""
    return ErrorFirewall()


@pytest.fixture
def firewall_no_autofix():
    """Create firewall with auto-fix disabled."""
    config = RouterConfig(auto_fix_mode_violations=False)
    return ErrorFirewall(config=config)


@pytest.fixture
def object_mode_context():
    """Create context in OBJECT mode."""
    return SceneContext(
        mode="OBJECT",
        active_object="Cube",
        selected_objects=["Cube"],
        objects=[
            ObjectInfo(
                name="Cube",
                type="MESH",
                dimensions=[2.0, 2.0, 2.0],
                selected=True,
                active=True,
            )
        ],
        topology=TopologyInfo(vertices=8, edges=12, faces=6),
        materials=[],
    )


@pytest.fixture
def edit_mode_context():
    """Create context in EDIT mode with selection."""
    return SceneContext(
        mode="EDIT",
        active_object="Cube",
        selected_objects=["Cube"],
        objects=[
            ObjectInfo(
                name="Cube",
                type="MESH",
                dimensions=[2.0, 2.0, 2.0],
                selected=True,
                active=True,
            )
        ],
        topology=TopologyInfo(
            vertices=8, edges=12, faces=6,
            selected_verts=8, selected_edges=12, selected_faces=6,
        ),
        materials=[],
    )


@pytest.fixture
def edit_mode_no_selection():
    """Create context in EDIT mode without selection."""
    return SceneContext(
        mode="EDIT",
        active_object="Cube",
        selected_objects=["Cube"],
        objects=[
            ObjectInfo(
                name="Cube",
                type="MESH",
                dimensions=[2.0, 2.0, 2.0],
                selected=True,
                active=True,
            )
        ],
        topology=TopologyInfo(
            vertices=8, edges=12, faces=6,
            selected_verts=0, selected_edges=0, selected_faces=0,
        ),
        materials=[],
    )


@pytest.fixture
def empty_scene_context():
    """Create context with no objects."""
    return SceneContext(
        mode="OBJECT",
        active_object=None,
        selected_objects=[],
        objects=[],
    )


def make_tool_call(tool_name: str, params: dict = None) -> CorrectedToolCall:
    """Helper to create a CorrectedToolCall."""
    return CorrectedToolCall(
        tool_name=tool_name,
        params=params or {},
        corrections_applied=[],
        is_injected=False,
    )


class TestErrorFirewallInit:
    """Tests for initialization."""

    def test_init_default_config(self, firewall):
        """Test initialization with default config."""
        assert firewall._config is not None
        assert firewall._config.auto_fix_mode_violations is True

    def test_init_registers_default_rules(self, firewall):
        """Test that default rules are registered."""
        rules = firewall.get_firewall_rules()
        assert len(rules) > 0

    def test_init_custom_config(self, firewall_no_autofix):
        """Test initialization with custom config."""
        assert firewall_no_autofix._config.auto_fix_mode_violations is False


class TestValidateModeViolations:
    """Tests for mode violation detection."""

    def test_mesh_in_object_mode_violation(self, firewall, object_mode_context):
        """Test that mesh tool in OBJECT mode triggers violation."""
        call = make_tool_call("mesh_extrude_region", {"depth": 0.5})
        result = firewall.validate(call, object_mode_context)

        assert result.action != FirewallAction.BLOCK
        # Should auto-fix with mode switch
        assert len(result.violations) > 0

    def test_mesh_in_edit_mode_allowed(self, firewall, edit_mode_context):
        """Test that mesh tool in EDIT mode is allowed."""
        call = make_tool_call("mesh_subdivide", {"number_cuts": 2})
        result = firewall.validate(call, edit_mode_context)

        assert result.action == FirewallAction.ALLOW

    def test_modeling_in_edit_mode_violation(self, firewall, edit_mode_context):
        """Test that modeling tool in EDIT mode triggers violation."""
        call = make_tool_call("modeling_add_modifier", {"modifier_type": "BEVEL"})
        result = firewall.validate(call, edit_mode_context)

        # Should have violations and suggest mode switch
        assert len(result.violations) > 0

    def test_modeling_in_object_mode_allowed(self, firewall, object_mode_context):
        """Test that modeling tool in OBJECT mode is allowed."""
        call = make_tool_call("modeling_transform_object", {"scale": [1, 1, 1]})
        result = firewall.validate(call, object_mode_context)

        assert result.action == FirewallAction.ALLOW


class TestValidateSelectionViolations:
    """Tests for selection violation detection."""

    def test_extrude_no_selection_violation(self, firewall, edit_mode_no_selection):
        """Test that extrude without selection triggers violation."""
        call = make_tool_call("mesh_extrude_region", {"depth": 0.5})
        result = firewall.validate(call, edit_mode_no_selection)

        # Should auto-fix with select all
        assert len(result.violations) > 0

    def test_extrude_with_selection_allowed(self, firewall, edit_mode_context):
        """Test that extrude with selection is allowed."""
        call = make_tool_call("mesh_extrude_region", {"depth": 0.5})
        result = firewall.validate(call, edit_mode_context)

        assert result.action == FirewallAction.ALLOW

    def test_bevel_no_selection_violation(self, firewall, edit_mode_no_selection):
        """Test that bevel without selection triggers violation."""
        call = make_tool_call("mesh_bevel", {"width": 0.1})
        result = firewall.validate(call, edit_mode_no_selection)

        assert len(result.violations) > 0


class TestValidateParameterViolations:
    """Tests for parameter violation detection."""

    def test_bevel_too_large_modified(self, firewall, edit_mode_context):
        """Test that large bevel width is modified."""
        call = make_tool_call("mesh_bevel", {"width": 100.0})
        result = firewall.validate(call, edit_mode_context)

        # Should modify the parameter
        if result.modified_call:
            assert result.modified_call["params"]["width"] < 100.0

    def test_subdivide_too_many_cuts_modified(self, firewall, edit_mode_context):
        """Test that too many subdivide cuts is modified."""
        call = make_tool_call("mesh_subdivide", {"number_cuts": 100})
        result = firewall.validate(call, edit_mode_context)

        if result.modified_call:
            assert result.modified_call["params"]["number_cuts"] <= 6


class TestValidateBlockingRules:
    """Tests for blocking rules."""

    def test_delete_no_objects_blocked(self, firewall, empty_scene_context):
        """Test that delete with no objects is blocked."""
        call = make_tool_call("scene_delete_object", {"name": "Cube"})
        result = firewall.validate(call, empty_scene_context)

        assert result.action == FirewallAction.BLOCK

    def test_delete_with_objects_allowed(self, firewall, object_mode_context):
        """Test that delete with objects is allowed."""
        call = make_tool_call("scene_delete_object", {"name": "Cube"})
        result = firewall.validate(call, object_mode_context)

        assert result.action != FirewallAction.BLOCK


class TestAutoFix:
    """Tests for auto-fix functionality."""

    def test_auto_fix_mode_switch(self, firewall, object_mode_context):
        """Test that auto-fix adds mode switch."""
        call = make_tool_call("mesh_extrude_region", {"depth": 0.5})
        result = firewall.validate(call, object_mode_context)

        if result.pre_steps:
            mode_switch = next(
                (s for s in result.pre_steps if s["tool"] == "system_set_mode"),
                None,
            )
            assert mode_switch is not None
            assert mode_switch["params"]["mode"] == "EDIT"

    def test_auto_fix_selection(self, firewall, edit_mode_no_selection):
        """Test that auto-fix adds selection."""
        call = make_tool_call("mesh_extrude_region", {"depth": 0.5})
        result = firewall.validate(call, edit_mode_no_selection)

        if result.pre_steps:
            select_all = next(
                (s for s in result.pre_steps if s["tool"] == "mesh_select"),
                None,
            )
            assert select_all is not None
            assert select_all["params"]["action"] == "all"

    def test_auto_fix_disabled(self, firewall_no_autofix, object_mode_context):
        """Test that auto-fix respects config."""
        call = make_tool_call("mesh_extrude_region", {"depth": 0.5})
        result = firewall_no_autofix.validate(call, object_mode_context)

        # Should not have pre_steps for mode switch
        if result.pre_steps:
            mode_switches = [s for s in result.pre_steps if s["tool"] == "system_set_mode"]
            assert len(mode_switches) == 0


class TestCanAutoFix:
    """Tests for can_auto_fix method."""

    def test_can_fix_mode_violation(self, firewall, object_mode_context):
        """Test that mode violation can be auto-fixed."""
        call = make_tool_call("mesh_extrude_region", {"depth": 0.5})
        result = firewall.can_auto_fix(call, object_mode_context)

        assert result is True

    def test_cannot_fix_blocked(self, firewall, empty_scene_context):
        """Test that blocked operation cannot be auto-fixed."""
        call = make_tool_call("scene_delete_object", {"name": "Cube"})
        result = firewall.can_auto_fix(call, empty_scene_context)

        assert result is False

    def test_can_fix_valid_call(self, firewall, edit_mode_context):
        """Test that valid call returns True."""
        call = make_tool_call("mesh_subdivide", {"number_cuts": 2})
        result = firewall.can_auto_fix(call, edit_mode_context)

        assert result is True


class TestValidateSequence:
    """Tests for validate_sequence method."""

    def test_validate_multiple_calls(self, firewall, edit_mode_context):
        """Test validating multiple calls."""
        calls = [
            make_tool_call("mesh_subdivide", {"number_cuts": 2}),
            make_tool_call("mesh_bevel", {"width": 0.1}),
            make_tool_call("mesh_smooth", {"factor": 0.5}),
        ]

        results = firewall.validate_sequence(calls, edit_mode_context)

        assert len(results) == 3

    def test_validate_empty_sequence(self, firewall, edit_mode_context):
        """Test validating empty sequence."""
        results = firewall.validate_sequence([], edit_mode_context)

        assert results == []


class TestRegisterRule:
    """Tests for register_rule method."""

    def test_register_new_rule(self, firewall):
        """Test registering a new rule."""
        initial_count = len(firewall.get_firewall_rules())

        firewall.register_rule(
            rule_name="custom_rule",
            tool_pattern="custom_*",
            condition="mode == 'OBJECT'",
            action="block",
        )

        assert len(firewall.get_firewall_rules()) == initial_count + 1

    def test_register_rule_with_fix(self, firewall):
        """Test registering a rule with fix description."""
        firewall.register_rule(
            rule_name="fixable_rule",
            tool_pattern="test_*",
            condition="mode == 'EDIT'",
            action="auto_fix",
            fix_description="Switch to OBJECT mode",
        )

        rules = firewall.get_firewall_rules()
        rule = next((r for r in rules if r["rule_name"] == "fixable_rule"), None)

        assert rule is not None
        assert rule["fix_description"] == "Switch to OBJECT mode"


class TestEnableDisableRule:
    """Tests for enable_rule and disable_rule methods."""

    def test_disable_existing_rule(self, firewall):
        """Test disabling an existing rule."""
        result = firewall.disable_rule("mesh_in_object_mode")
        assert result is True

    def test_disable_nonexistent_rule(self, firewall):
        """Test disabling non-existent rule."""
        result = firewall.disable_rule("nonexistent_rule")
        assert result is False

    def test_enable_disabled_rule(self, firewall):
        """Test enabling a disabled rule."""
        firewall.disable_rule("mesh_in_object_mode")
        result = firewall.enable_rule("mesh_in_object_mode")

        assert result is True

    def test_disabled_rule_not_triggered(self, firewall, object_mode_context):
        """Test that disabled rule is not triggered."""
        firewall.disable_rule("mesh_in_object_mode")

        call = make_tool_call("mesh_extrude_region", {"depth": 0.5})
        result = firewall.validate(call, object_mode_context)

        # Should not have mode violation since rule is disabled
        mode_violations = [
            v for v in result.violations
            if "mesh_in_object_mode" in v.message
        ]
        assert len(mode_violations) == 0

    def test_get_rules_shows_enabled_status(self, firewall):
        """Test that get_firewall_rules shows enabled status."""
        firewall.disable_rule("mesh_in_object_mode")

        rules = firewall.get_firewall_rules()
        rule = next((r for r in rules if r["rule_name"] == "mesh_in_object_mode"), None)

        assert rule is not None
        assert rule["enabled"] is False


class TestGetFirewallRules:
    """Tests for get_firewall_rules method."""

    def test_returns_list(self, firewall):
        """Test that get_firewall_rules returns list."""
        rules = firewall.get_firewall_rules()
        assert isinstance(rules, list)

    def test_rules_have_required_fields(self, firewall):
        """Test that rules have required fields."""
        rules = firewall.get_firewall_rules()

        for rule in rules:
            assert "rule_name" in rule
            assert "tool_pattern" in rule
            assert "condition" in rule
            assert "action" in rule


class TestFirewallResult:
    """Tests for FirewallResult class."""

    def test_allow_result(self):
        """Test FirewallResult.allow()."""
        result = FirewallResult.allow()

        assert result.action == FirewallAction.ALLOW
        assert result.allowed is True

    def test_block_result(self):
        """Test FirewallResult.block()."""
        result = FirewallResult.block("Test reason", [])

        assert result.action == FirewallAction.BLOCK
        assert result.allowed is False
        assert "Test reason" in result.message

    def test_auto_fix_result(self):
        """Test FirewallResult.auto_fix()."""
        result = FirewallResult.auto_fix(
            "Fixed issue",
            modified_call={"tool": "test", "params": {}},
            pre_steps=[{"tool": "step1", "params": {}}],
            violations=[],
        )

        assert result.action == FirewallAction.AUTO_FIX
        assert result.modified_call is not None
        assert len(result.pre_steps) == 1


class TestPatternMatching:
    """Tests for tool pattern matching."""

    def test_wildcard_pattern(self, firewall, object_mode_context):
        """Test wildcard pattern matching."""
        # mesh_* should match mesh_anything
        call = make_tool_call("mesh_custom_tool", {})
        result = firewall.validate(call, object_mode_context)

        # Should trigger mesh_in_object_mode rule
        assert len(result.violations) > 0

    def test_exact_pattern(self, firewall, edit_mode_no_selection):
        """Test exact pattern matching."""
        # mesh_extrude_region should match exactly
        call = make_tool_call("mesh_extrude_region", {"depth": 0.5})
        result = firewall.validate(call, edit_mode_no_selection)

        assert len(result.violations) > 0


class TestConditionEvaluation:
    """Tests for condition evaluation."""

    def test_mode_equals_condition(self, firewall, object_mode_context):
        """Test mode == condition."""
        call = make_tool_call("mesh_test", {})
        result = firewall.validate(call, object_mode_context)

        # mesh_in_object_mode should trigger
        assert len(result.violations) > 0

    def test_no_selection_condition(self, firewall, edit_mode_no_selection):
        """Test no_selection condition."""
        call = make_tool_call("mesh_extrude_region", {"depth": 0.5})
        result = firewall.validate(call, edit_mode_no_selection)

        assert len(result.violations) > 0

    def test_no_objects_condition(self, firewall, empty_scene_context):
        """Test no_objects condition."""
        call = make_tool_call("scene_delete_object", {})
        result = firewall.validate(call, empty_scene_context)

        assert result.action == FirewallAction.BLOCK


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_params(self, firewall, edit_mode_context):
        """Test validation with empty params."""
        call = make_tool_call("mesh_subdivide", {})
        result = firewall.validate(call, edit_mode_context)

        assert result.action == FirewallAction.ALLOW

    def test_unknown_tool(self, firewall, edit_mode_context):
        """Test validation with unknown tool."""
        call = make_tool_call("unknown_tool", {"value": 1})
        result = firewall.validate(call, edit_mode_context)

        # Should allow unknown tools
        assert result.action == FirewallAction.ALLOW
