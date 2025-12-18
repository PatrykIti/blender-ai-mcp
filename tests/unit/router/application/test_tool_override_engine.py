"""
Unit tests for ToolOverrideEngine.

Tests tool replacement logic and override rules.
"""

import pytest

from server.router.application.engines.tool_override_engine import ToolOverrideEngine
from server.router.domain.entities.scene_context import (
    SceneContext,
    ObjectInfo,
    TopologyInfo,
)
from server.router.domain.entities.pattern import DetectedPattern, PatternType
from server.router.domain.entities.override_decision import OverrideDecision
from server.router.infrastructure.config import RouterConfig


@pytest.fixture
def engine():
    """Create a ToolOverrideEngine with default config."""
    return ToolOverrideEngine()


@pytest.fixture
def engine_disabled():
    """Create engine with overrides disabled."""
    config = RouterConfig(enable_overrides=False)
    return ToolOverrideEngine(config=config)


@pytest.fixture
def base_context():
    """Create a base scene context."""
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
def phone_pattern():
    """Create a phone_like pattern."""
    return DetectedPattern(
        pattern_type=PatternType.PHONE_LIKE,
        confidence=0.85,
        metadata={"aspect_xy": 0.5, "is_flat": True},
    )


@pytest.fixture
def tower_pattern():
    """Create a tower_like pattern."""
    return DetectedPattern(
        pattern_type=PatternType.TOWER_LIKE,
        confidence=0.90,
        metadata={"aspect_ratio": 6.0, "is_tall": True},
    )


class TestToolOverrideEngineInit:
    """Tests for initialization."""

    def test_init_default_config(self, engine):
        """Test initialization with default config."""
        assert engine._config is not None
        assert engine._config.enable_overrides is True

    def test_init_registers_default_rules(self, engine):
        """Test that default rules are registered."""
        rules = engine.get_override_rules()
        assert len(rules) > 0

    def test_init_custom_config(self, engine_disabled):
        """Test initialization with overrides disabled."""
        assert engine_disabled._config.enable_overrides is False


class TestCheckOverride:
    """Tests for check_override method."""

    def test_no_override_without_pattern(self, engine, base_context):
        """Test no override when no pattern detected."""
        decision = engine.check_override(
            "mesh_extrude_region",
            {"move": [0.0, 0.0, 0.5]},
            base_context,
            pattern=None,
        )

        assert decision.should_override is False

    def test_override_with_phone_pattern(self, engine, base_context, phone_pattern):
        """Test override triggered with phone pattern."""
        decision = engine.check_override(
            "mesh_extrude_region",
            {"move": [0.0, 0.0, -0.02]},
            base_context,
            pattern=phone_pattern,
        )

        assert decision.should_override is True
        assert len(decision.replacement_tools) > 0

    def test_override_with_tower_pattern(self, engine, base_context, tower_pattern):
        """Test override triggered with tower pattern."""
        decision = engine.check_override(
            "mesh_subdivide",
            {"number_cuts": 3},
            base_context,
            pattern=tower_pattern,
        )

        assert decision.should_override is True
        assert len(decision.replacement_tools) > 0

    def test_no_override_wrong_tool(self, engine, base_context, phone_pattern):
        """Test no override when tool doesn't match."""
        decision = engine.check_override(
            "mesh_bevel",
            {"offset": 0.1},
            base_context,
            pattern=phone_pattern,
        )

        assert decision.should_override is False

    def test_no_override_wrong_pattern(self, engine, base_context, tower_pattern):
        """Test no override when pattern doesn't match."""
        decision = engine.check_override(
            "mesh_extrude_region",
            {"move": [0.0, 0.0, 0.5]},
            base_context,
            pattern=tower_pattern,  # extrude is for phone, not tower
        )

        assert decision.should_override is False

    def test_override_disabled(self, engine_disabled, base_context, phone_pattern):
        """Test that disabled overrides return no override."""
        decision = engine_disabled.check_override(
            "mesh_extrude_region",
            {"move": [0.0, 0.0, 0.5]},
            base_context,
            pattern=phone_pattern,
        )

        assert decision.should_override is False


class TestOverrideDecisionContent:
    """Tests for override decision content."""

    def test_phone_override_has_inset(self, engine, base_context, phone_pattern):
        """Test phone override includes inset."""
        decision = engine.check_override(
            "mesh_extrude_region",
            {"move": [0.0, 0.0, -0.02]},
            base_context,
            pattern=phone_pattern,
        )

        tool_names = [t.tool_name for t in decision.replacement_tools]
        assert "mesh_inset" in tool_names

    def test_phone_override_has_extrude(self, engine, base_context, phone_pattern):
        """Test phone override includes extrude."""
        decision = engine.check_override(
            "mesh_extrude_region",
            {"move": [0.0, 0.0, -0.02]},
            base_context,
            pattern=phone_pattern,
        )

        tool_names = [t.tool_name for t in decision.replacement_tools]
        assert "mesh_extrude_region" in tool_names

    def test_tower_override_has_subdivide(self, engine, base_context, tower_pattern):
        """Test tower override includes subdivide."""
        decision = engine.check_override(
            "mesh_subdivide",
            {"number_cuts": 3},
            base_context,
            pattern=tower_pattern,
        )

        tool_names = [t.tool_name for t in decision.replacement_tools]
        assert "mesh_subdivide" in tool_names

    def test_tower_override_has_transform(self, engine, base_context, tower_pattern):
        """Test tower override includes transform for taper."""
        decision = engine.check_override(
            "mesh_subdivide",
            {"number_cuts": 3},
            base_context,
            pattern=tower_pattern,
        )

        tool_names = [t.tool_name for t in decision.replacement_tools]
        assert "mesh_transform_selected" in tool_names

    def test_override_has_reasons(self, engine, base_context, phone_pattern):
        """Test override decision has reasons."""
        decision = engine.check_override(
            "mesh_extrude_region",
            {"move": [0.0, 0.0, -0.02]},
            base_context,
            pattern=phone_pattern,
        )

        assert len(decision.reasons) > 0
        assert decision.reasons[0].rule_name == "extrude_for_screen"


class TestRegisterRule:
    """Tests for register_rule method."""

    def test_register_new_rule(self, engine):
        """Test registering a new override rule."""
        engine.register_rule(
            rule_name="custom_rule",
            trigger_tool="mesh_bevel",
            trigger_pattern="custom_pattern",
            replacement_tools=[
                {"tool_name": "mesh_smooth", "params": {"factor": 0.5}},
            ],
        )

        rules = engine.get_override_rules()
        rule_names = [r["rule_name"] for r in rules]
        assert "custom_rule" in rule_names

    def test_register_rule_without_pattern(self, engine, base_context):
        """Test registering rule without pattern requirement."""
        engine.register_rule(
            rule_name="always_smooth",
            trigger_tool="mesh_bevel",
            trigger_pattern=None,
            replacement_tools=[
                {"tool_name": "mesh_smooth", "params": {}},
            ],
        )

        decision = engine.check_override(
            "mesh_bevel",
            {"offset": 0.1},
            base_context,
            pattern=None,
        )

        assert decision.should_override is True

    def test_overwrite_existing_rule(self, engine):
        """Test that registering with same name overwrites."""
        initial_count = len(engine.get_override_rules())

        engine.register_rule(
            rule_name="extrude_for_screen",
            trigger_tool="mesh_extrude_region",
            trigger_pattern="phone_like",
            replacement_tools=[
                {"tool_name": "mesh_new_tool", "params": {}},
            ],
        )

        assert len(engine.get_override_rules()) == initial_count


class TestRemoveRule:
    """Tests for remove_rule method."""

    def test_remove_existing_rule(self, engine):
        """Test removing an existing rule."""
        initial_count = len(engine.get_override_rules())
        result = engine.remove_rule("extrude_for_screen")

        assert result is True
        assert len(engine.get_override_rules()) == initial_count - 1

    def test_remove_nonexistent_rule(self, engine):
        """Test removing a non-existent rule."""
        result = engine.remove_rule("nonexistent_rule")

        assert result is False

    def test_removed_rule_no_override(self, engine, base_context, phone_pattern):
        """Test that removed rule doesn't trigger override."""
        engine.remove_rule("extrude_for_screen")

        decision = engine.check_override(
            "mesh_extrude_region",
            {"move": [0.0, 0.0, -0.02]},
            base_context,
            pattern=phone_pattern,
        )

        assert decision.should_override is False


class TestGetOverrideRules:
    """Tests for get_override_rules method."""

    def test_returns_list(self, engine):
        """Test that get_override_rules returns a list."""
        rules = engine.get_override_rules()
        assert isinstance(rules, list)

    def test_rules_have_required_fields(self, engine):
        """Test that rules have required fields."""
        rules = engine.get_override_rules()

        for rule in rules:
            assert "rule_name" in rule
            assert "trigger_tool" in rule
            assert "replacement_tools" in rule


class TestReplacementToolInheritance:
    """Tests for parameter inheritance in replacements."""

    def test_inherit_params_specified(self, engine, base_context, phone_pattern):
        """Test that inherit_params field is present."""
        decision = engine.check_override(
            "mesh_extrude_region",
            {"move": [0.0, 0.0, -0.02]},
            base_context,
            pattern=phone_pattern,
        )

        # Find extrude in replacement tools
        extrude_tool = next(
            (t for t in decision.replacement_tools if t.tool_name == "mesh_extrude_region"),
            None,
        )

        assert extrude_tool is not None
        assert "move" in extrude_tool.inherit_params

    def test_replacement_has_description(self, engine, base_context, phone_pattern):
        """Test that replacement tools have descriptions."""
        decision = engine.check_override(
            "mesh_extrude_region",
            {"move": [0.0, 0.0, -0.02]},
            base_context,
            pattern=phone_pattern,
        )

        for tool in decision.replacement_tools:
            assert tool.description != ""


class TestNoOverrideDecision:
    """Tests for OverrideDecision.no_override()."""

    def test_no_override_static_method(self):
        """Test no_override static method."""
        decision = OverrideDecision.no_override()

        assert decision.should_override is False
        assert decision.replacement_tools == []
        assert decision.reasons == []


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_params(self, engine, base_context, phone_pattern):
        """Test override with empty params."""
        decision = engine.check_override(
            "mesh_extrude_region",
            {},
            base_context,
            pattern=phone_pattern,
        )

        assert decision.should_override is True

    def test_pattern_with_unknown_type(self, engine, base_context):
        """Test override with unknown pattern type."""
        pattern = DetectedPattern(
            pattern_type=PatternType.UNKNOWN,
            confidence=0.5,
            metadata={},
        )

        decision = engine.check_override(
            "mesh_extrude_region",
            {"move": [0.0, 0.0, 0.5]},
            base_context,
            pattern=pattern,
        )

        assert decision.should_override is False
