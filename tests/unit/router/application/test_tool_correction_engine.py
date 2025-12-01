"""
Unit tests for ToolCorrectionEngine.

Tests parameter clamping, mode switching, and selection handling.
"""

import pytest
from unittest.mock import MagicMock

from server.router.application.engines.tool_correction_engine import (
    ToolCorrectionEngine,
    MODE_REQUIREMENTS,
    PARAM_LIMITS,
    SELECTION_REQUIRED_TOOLS,
)
from server.router.domain.entities.scene_context import (
    SceneContext,
    ObjectInfo,
    TopologyInfo,
)
from server.router.infrastructure.config import RouterConfig


@pytest.fixture
def engine():
    """Create a ToolCorrectionEngine with default config."""
    return ToolCorrectionEngine()


@pytest.fixture
def engine_no_auto():
    """Create engine with auto-fixes disabled."""
    config = RouterConfig(
        auto_mode_switch=False,
        auto_selection=False,
        clamp_parameters=False,
    )
    return ToolCorrectionEngine(config=config)


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


class TestToolCorrectionEngineInit:
    """Tests for initialization."""

    def test_init_default_config(self, engine):
        """Test initialization with default config."""
        assert engine._config is not None
        assert engine._config.auto_mode_switch is True
        assert engine._config.auto_selection is True
        assert engine._config.clamp_parameters is True

    def test_init_custom_config(self, engine_no_auto):
        """Test initialization with custom config."""
        assert engine_no_auto._config.auto_mode_switch is False
        assert engine_no_auto._config.auto_selection is False
        assert engine_no_auto._config.clamp_parameters is False


class TestModeRequirements:
    """Tests for get_required_mode."""

    def test_mesh_tools_require_edit(self, engine):
        """Test that mesh tools require EDIT mode."""
        assert engine.get_required_mode("mesh_extrude_region") == "EDIT"
        assert engine.get_required_mode("mesh_bevel") == "EDIT"
        assert engine.get_required_mode("mesh_subdivide") == "EDIT"

    def test_modeling_tools_require_object(self, engine):
        """Test that modeling tools require OBJECT mode."""
        assert engine.get_required_mode("modeling_create_primitive") == "OBJECT"
        assert engine.get_required_mode("modeling_add_modifier") == "OBJECT"
        assert engine.get_required_mode("modeling_transform_object") == "OBJECT"

    def test_sculpt_tools_require_sculpt(self, engine):
        """Test that sculpt tools require SCULPT mode."""
        assert engine.get_required_mode("sculpt_draw") == "SCULPT"
        assert engine.get_required_mode("sculpt_smooth") == "SCULPT"

    def test_scene_tools_require_object(self, engine):
        """Test that scene tools require OBJECT mode."""
        assert engine.get_required_mode("scene_delete_object") == "OBJECT"
        assert engine.get_required_mode("scene_create") == "OBJECT"

    def test_system_tools_allow_any(self, engine):
        """Test that system tools allow ANY mode."""
        assert engine.get_required_mode("system_set_mode") == "ANY"

    def test_unknown_tools_allow_any(self, engine):
        """Test that unknown tools allow ANY mode."""
        assert engine.get_required_mode("unknown_tool") == "ANY"
        assert engine.get_required_mode("custom_operation") == "ANY"


class TestSelectionRequirements:
    """Tests for requires_selection."""

    def test_extrude_requires_selection(self, engine):
        """Test that extrude requires selection."""
        assert engine.requires_selection("mesh_extrude_region") is True

    def test_bevel_requires_selection(self, engine):
        """Test that bevel requires selection."""
        assert engine.requires_selection("mesh_bevel") is True

    def test_subdivide_no_selection(self, engine):
        """Test that subdivide doesn't require selection."""
        assert engine.requires_selection("mesh_subdivide") is False

    def test_selection_tools_list(self, engine):
        """Test all tools in SELECTION_REQUIRED_TOOLS."""
        for tool in SELECTION_REQUIRED_TOOLS:
            assert engine.requires_selection(tool) is True


class TestModeSwitch:
    """Tests for automatic mode switching."""

    def test_mesh_tool_in_object_mode_adds_switch(self, engine, object_mode_context):
        """Test that mesh tool in OBJECT mode adds mode switch."""
        corrected, pre_steps = engine.correct(
            "mesh_extrude_region",
            {"depth": 0.5},
            object_mode_context,
        )

        assert len(pre_steps) == 1
        assert pre_steps[0].tool_name == "system_set_mode"
        assert pre_steps[0].params["mode"] == "EDIT"
        assert "mode_switch:OBJECT->EDIT" in corrected.corrections_applied

    def test_modeling_tool_in_edit_mode_adds_switch(self, engine, edit_mode_context):
        """Test that modeling tool in EDIT mode adds mode switch."""
        corrected, pre_steps = engine.correct(
            "modeling_add_modifier",
            {"modifier_type": "BEVEL"},
            edit_mode_context,
        )

        assert len(pre_steps) >= 1
        mode_switch = next(
            (s for s in pre_steps if s.tool_name == "system_set_mode"),
            None,
        )
        assert mode_switch is not None
        assert mode_switch.params["mode"] == "OBJECT"

    def test_correct_mode_no_switch(self, engine, edit_mode_context):
        """Test that correct mode doesn't add switch."""
        corrected, pre_steps = engine.correct(
            "mesh_subdivide",
            {"number_cuts": 2},
            edit_mode_context,
        )

        mode_switches = [s for s in pre_steps if s.tool_name == "system_set_mode"]
        assert len(mode_switches) == 0

    def test_mode_switch_disabled(self, engine_no_auto, object_mode_context):
        """Test that mode switch respects config."""
        corrected, pre_steps = engine_no_auto.correct(
            "mesh_extrude_region",
            {"depth": 0.5},
            object_mode_context,
        )

        mode_switches = [s for s in pre_steps if s.tool_name == "system_set_mode"]
        assert len(mode_switches) == 0


class TestAutoSelection:
    """Tests for automatic selection."""

    def test_extrude_no_selection_adds_select(self, engine, edit_mode_no_selection):
        """Test that extrude without selection adds select all."""
        corrected, pre_steps = engine.correct(
            "mesh_extrude_region",
            {"depth": 0.5},
            edit_mode_no_selection,
        )

        select_calls = [s for s in pre_steps if s.tool_name == "mesh_select"]
        assert len(select_calls) == 1
        assert select_calls[0].params["action"] == "all"
        assert "auto_select_all" in corrected.corrections_applied

    def test_bevel_no_selection_adds_select(self, engine, edit_mode_no_selection):
        """Test that bevel without selection adds select all."""
        corrected, pre_steps = engine.correct(
            "mesh_bevel",
            {"width": 0.1},
            edit_mode_no_selection,
        )

        select_calls = [s for s in pre_steps if s.tool_name == "mesh_select"]
        assert len(select_calls) == 1

    def test_has_selection_no_extra_select(self, engine, edit_mode_context):
        """Test that existing selection doesn't add select."""
        corrected, pre_steps = engine.correct(
            "mesh_extrude_region",
            {"depth": 0.5},
            edit_mode_context,
        )

        select_calls = [s for s in pre_steps if s.tool_name == "mesh_select"]
        assert len(select_calls) == 0

    def test_auto_selection_disabled(self, engine_no_auto, edit_mode_no_selection):
        """Test that auto selection respects config."""
        corrected, pre_steps = engine_no_auto.correct(
            "mesh_extrude_region",
            {"depth": 0.5},
            edit_mode_no_selection,
        )

        select_calls = [s for s in pre_steps if s.tool_name == "mesh_select"]
        assert len(select_calls) == 0


class TestParameterClamping:
    """Tests for parameter clamping."""

    def test_bevel_width_clamped_high(self, engine, edit_mode_context):
        """Test that bevel width is clamped to max."""
        corrected, _ = engine.correct(
            "mesh_bevel",
            {"width": 100.0, "segments": 3},
            edit_mode_context,
        )

        # Should be clamped based on dimension ratio
        assert corrected.params["width"] < 100.0
        assert any("clamp_width" in c for c in corrected.corrections_applied)

    def test_bevel_width_clamped_low(self, engine, edit_mode_context):
        """Test that bevel width is clamped to min."""
        corrected, _ = engine.correct(
            "mesh_bevel",
            {"width": 0.0001, "segments": 3},
            edit_mode_context,
        )

        assert corrected.params["width"] >= 0.001

    def test_bevel_segments_clamped(self, engine, edit_mode_context):
        """Test that bevel segments are clamped."""
        corrected, _ = engine.correct(
            "mesh_bevel",
            {"width": 0.1, "segments": 50},
            edit_mode_context,
        )

        assert corrected.params["segments"] <= 10

    def test_subdivide_cuts_clamped(self, engine, edit_mode_context):
        """Test that subdivide cuts are clamped."""
        corrected, _ = engine.correct(
            "mesh_subdivide",
            {"number_cuts": 100},
            edit_mode_context,
        )

        assert corrected.params["number_cuts"] <= 6

    def test_valid_params_unchanged(self, engine, edit_mode_context):
        """Test that valid params are not changed."""
        original_params = {"width": 0.1, "segments": 3}
        corrected, _ = engine.correct(
            "mesh_bevel",
            original_params.copy(),
            edit_mode_context,
        )

        assert corrected.params["width"] == 0.1
        assert corrected.params["segments"] == 3

    def test_clamping_disabled(self, engine_no_auto, edit_mode_context):
        """Test that clamping respects config."""
        corrected, _ = engine_no_auto.correct(
            "mesh_bevel",
            {"width": 100.0, "segments": 50},
            edit_mode_context,
        )

        assert corrected.params["width"] == 100.0
        assert corrected.params["segments"] == 50


class TestCorrectedToolCall:
    """Tests for CorrectedToolCall output."""

    def test_preserves_tool_name(self, engine, edit_mode_context):
        """Test that tool name is preserved."""
        corrected, _ = engine.correct(
            "mesh_subdivide",
            {"number_cuts": 2},
            edit_mode_context,
        )

        assert corrected.tool_name == "mesh_subdivide"

    def test_preserves_original_params(self, engine, edit_mode_context):
        """Test that original params are preserved."""
        original = {"width": 100.0, "segments": 50}
        corrected, _ = engine.correct(
            "mesh_bevel",
            original,
            edit_mode_context,
        )

        assert corrected.original_params == original

    def test_not_injected(self, engine, edit_mode_context):
        """Test that corrected call is not marked as injected."""
        corrected, _ = engine.correct(
            "mesh_subdivide",
            {},
            edit_mode_context,
        )

        assert corrected.is_injected is False

    def test_pre_steps_are_injected(self, engine, object_mode_context):
        """Test that pre-steps are marked as injected."""
        _, pre_steps = engine.correct(
            "mesh_extrude_region",
            {"depth": 0.5},
            object_mode_context,
        )

        for step in pre_steps:
            assert step.is_injected is True


class TestHelperMethods:
    """Tests for helper methods."""

    def test_get_mode_switch_call(self, engine):
        """Test mode switch call generation."""
        call = engine.get_mode_switch_call("EDIT")

        assert call.tool_name == "system_set_mode"
        assert call.params["mode"] == "EDIT"
        assert call.is_injected is True

    def test_get_selection_call(self, engine):
        """Test selection call generation."""
        call = engine.get_selection_call("all")

        assert call.tool_name == "mesh_select"
        assert call.params["action"] == "all"
        assert call.is_injected is True

    def test_get_selection_call_none(self, engine):
        """Test selection call with none action."""
        call = engine.get_selection_call("none")

        assert call.params["action"] == "none"


class TestClampParameters:
    """Tests for clamp_parameters method directly."""

    def test_clamp_returns_tuple(self, engine, edit_mode_context):
        """Test that clamp returns tuple of params and corrections."""
        params, corrections = engine.clamp_parameters(
            "mesh_bevel",
            {"width": 0.1},
            edit_mode_context,
        )

        assert isinstance(params, dict)
        assert isinstance(corrections, list)

    def test_clamp_unknown_tool(self, engine, edit_mode_context):
        """Test clamping unknown tool params."""
        params, corrections = engine.clamp_parameters(
            "unknown_tool",
            {"value": 1000},
            edit_mode_context,
        )

        assert params["value"] == 1000
        assert len(corrections) == 0


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_params(self, engine, edit_mode_context):
        """Test correction with empty params."""
        corrected, pre_steps = engine.correct(
            "mesh_subdivide",
            {},
            edit_mode_context,
        )

        assert corrected.params == {}

    def test_none_params(self, engine, edit_mode_context):
        """Test correction with None params."""
        corrected, pre_steps = engine.correct(
            "mesh_subdivide",
            None,
            edit_mode_context,
        )

        assert corrected.params == {}

    def test_no_active_object(self, engine):
        """Test correction with no active object."""
        context = SceneContext(
            mode="OBJECT",
            active_object=None,
            selected_objects=[],
            objects=[],
        )

        corrected, pre_steps = engine.correct(
            "mesh_subdivide",
            {"number_cuts": 2},
            context,
        )

        assert corrected.tool_name == "mesh_subdivide"


class TestModeRequirementsConstant:
    """Tests for MODE_REQUIREMENTS constant."""

    def test_mode_requirements_has_mesh(self):
        """Test MODE_REQUIREMENTS has mesh prefix."""
        assert "mesh_" in MODE_REQUIREMENTS
        assert MODE_REQUIREMENTS["mesh_"] == "EDIT"

    def test_mode_requirements_has_modeling(self):
        """Test MODE_REQUIREMENTS has modeling prefix."""
        assert "modeling_" in MODE_REQUIREMENTS
        assert MODE_REQUIREMENTS["modeling_"] == "OBJECT"

    def test_mode_requirements_has_sculpt(self):
        """Test MODE_REQUIREMENTS has sculpt prefix."""
        assert "sculpt_" in MODE_REQUIREMENTS
        assert MODE_REQUIREMENTS["sculpt_"] == "SCULPT"


class TestParamLimitsConstant:
    """Tests for PARAM_LIMITS constant."""

    def test_param_limits_has_bevel(self):
        """Test PARAM_LIMITS has bevel limits."""
        assert "mesh_bevel" in PARAM_LIMITS
        assert "width" in PARAM_LIMITS["mesh_bevel"]
        assert "segments" in PARAM_LIMITS["mesh_bevel"]

    def test_param_limits_tuples(self):
        """Test PARAM_LIMITS values are tuples."""
        for tool, params in PARAM_LIMITS.items():
            for param, limits in params.items():
                assert isinstance(limits, tuple)
                assert len(limits) == 2
                assert limits[0] <= limits[1]
