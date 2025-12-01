"""
Tests for Router Domain Entities.

Task: TASK-039-2
"""

import pytest
from datetime import datetime

from server.router.domain.entities import (
    # Tool Call
    InterceptedToolCall,
    CorrectedToolCall,
    ToolCallSequence,
    # Scene Context
    ObjectInfo,
    TopologyInfo,
    ProportionInfo,
    SceneContext,
    # Pattern
    PatternType,
    DetectedPattern,
    PatternMatchResult,
    # Firewall
    FirewallAction,
    FirewallRuleType,
    FirewallViolation,
    FirewallResult,
    # Override
    OverrideReason,
    ReplacementTool,
    OverrideDecision,
)


class TestInterceptedToolCall:
    """Tests for InterceptedToolCall entity."""

    def test_create_basic(self):
        """Test basic creation."""
        call = InterceptedToolCall(
            tool_name="mesh_extrude",
            params={"value": 1.0},
        )
        assert call.tool_name == "mesh_extrude"
        assert call.params == {"value": 1.0}
        assert call.source == "llm"

    def test_create_with_all_fields(self):
        """Test creation with all fields."""
        timestamp = datetime.now()
        call = InterceptedToolCall(
            tool_name="mesh_bevel",
            params={"width": 0.1},
            timestamp=timestamp,
            source="router",
            original_prompt="bevel the edges",
            session_id="session-123",
        )
        assert call.timestamp == timestamp
        assert call.source == "router"
        assert call.original_prompt == "bevel the edges"
        assert call.session_id == "session-123"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        call = InterceptedToolCall(
            tool_name="mesh_extrude",
            params={"value": 1.0},
        )
        data = call.to_dict()
        assert data["tool_name"] == "mesh_extrude"
        assert data["params"] == {"value": 1.0}
        assert "timestamp" in data

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "tool_name": "mesh_inset",
            "params": {"thickness": 0.05},
            "source": "llm",
        }
        call = InterceptedToolCall.from_dict(data)
        assert call.tool_name == "mesh_inset"
        assert call.params == {"thickness": 0.05}


class TestCorrectedToolCall:
    """Tests for CorrectedToolCall entity."""

    def test_create_basic(self):
        """Test basic creation."""
        call = CorrectedToolCall(
            tool_name="mesh_extrude",
            params={"value": 1.0},
        )
        assert call.tool_name == "mesh_extrude"
        assert call.corrections_applied == []

    def test_with_corrections(self):
        """Test creation with corrections."""
        call = CorrectedToolCall(
            tool_name="mesh_extrude",
            params={"value": 0.5},
            corrections_applied=["clamped_value", "mode_switch"],
            original_params={"value": 100.0},
        )
        assert len(call.corrections_applied) == 2
        assert call.original_params == {"value": 100.0}

    def test_to_dict_for_execution(self):
        """Test conversion to execution format."""
        call = CorrectedToolCall(
            tool_name="mesh_bevel",
            params={"width": 0.1},
        )
        data = call.to_dict()
        assert data == {"tool": "mesh_bevel", "params": {"width": 0.1}}


class TestToolCallSequence:
    """Tests for ToolCallSequence entity."""

    def test_create_sequence(self):
        """Test creating a sequence."""
        calls = [
            CorrectedToolCall(tool_name="system_set_mode", params={"mode": "EDIT"}),
            CorrectedToolCall(tool_name="mesh_select", params={"action": "all"}),
            CorrectedToolCall(tool_name="mesh_extrude", params={"value": 1.0}),
        ]
        seq = ToolCallSequence(calls=calls)
        assert len(seq) == 3

    def test_iteration(self):
        """Test iterating over sequence."""
        calls = [
            CorrectedToolCall(tool_name="tool1", params={}),
            CorrectedToolCall(tool_name="tool2", params={}),
        ]
        seq = ToolCallSequence(calls=calls)
        names = [call.tool_name for call in seq]
        assert names == ["tool1", "tool2"]

    def test_to_execution_list(self):
        """Test conversion to execution list."""
        calls = [
            CorrectedToolCall(tool_name="tool1", params={"a": 1}),
            CorrectedToolCall(tool_name="tool2", params={"b": 2}),
        ]
        seq = ToolCallSequence(calls=calls)
        exec_list = seq.to_execution_list()
        assert exec_list == [
            {"tool": "tool1", "params": {"a": 1}},
            {"tool": "tool2", "params": {"b": 2}},
        ]


class TestSceneContext:
    """Tests for SceneContext entity."""

    def test_create_empty(self):
        """Test creating empty context."""
        ctx = SceneContext.empty()
        assert ctx.mode == "OBJECT"
        assert ctx.active_object is None

    def test_create_with_data(self):
        """Test creating context with data."""
        ctx = SceneContext(
            mode="EDIT",
            active_object="Cube",
            selected_objects=["Cube"],
        )
        assert ctx.mode == "EDIT"
        assert ctx.active_object == "Cube"
        assert ctx.is_edit_mode
        assert not ctx.is_object_mode

    def test_has_selection_object_mode(self):
        """Test has_selection in object mode."""
        ctx = SceneContext(
            mode="OBJECT",
            selected_objects=["Cube", "Sphere"],
        )
        assert ctx.has_selection

    def test_has_selection_edit_mode(self):
        """Test has_selection in edit mode."""
        topology = TopologyInfo(selected_verts=10)
        ctx = SceneContext(
            mode="EDIT",
            topology=topology,
        )
        assert ctx.has_selection

    def test_no_selection_edit_mode(self):
        """Test no selection in edit mode."""
        topology = TopologyInfo(vertices=100)
        ctx = SceneContext(
            mode="EDIT",
            topology=topology,
        )
        assert not ctx.has_selection


class TestTopologyInfo:
    """Tests for TopologyInfo entity."""

    def test_has_selection(self):
        """Test has_selection property."""
        topo = TopologyInfo(selected_verts=5, selected_edges=0, selected_faces=0)
        assert topo.has_selection

        topo2 = TopologyInfo(selected_verts=0, selected_edges=0, selected_faces=0)
        assert not topo2.has_selection

    def test_total_selected(self):
        """Test total_selected property."""
        topo = TopologyInfo(selected_verts=5, selected_edges=10, selected_faces=2)
        assert topo.total_selected == 17


class TestProportionInfo:
    """Tests for ProportionInfo entity."""

    def test_default_values(self):
        """Test default proportion values."""
        prop = ProportionInfo()
        assert prop.aspect_xy == 1.0
        assert prop.is_cubic

    def test_to_dict(self):
        """Test conversion to dictionary."""
        prop = ProportionInfo(
            aspect_xy=0.5,
            is_flat=True,
            dominant_axis="z",
        )
        data = prop.to_dict()
        assert data["aspect_xy"] == 0.5
        assert data["is_flat"] is True


class TestDetectedPattern:
    """Tests for DetectedPattern entity."""

    def test_create_pattern(self):
        """Test creating a pattern."""
        pattern = DetectedPattern(
            pattern_type=PatternType.PHONE_LIKE,
            confidence=0.85,
            suggested_workflow="phone_workflow",
        )
        assert pattern.name == "phone_like"
        assert pattern.is_confident

    def test_unknown_pattern(self):
        """Test creating unknown pattern."""
        pattern = DetectedPattern.unknown()
        assert pattern.pattern_type == PatternType.UNKNOWN
        assert pattern.confidence == 0.0
        assert not pattern.is_confident


class TestPatternMatchResult:
    """Tests for PatternMatchResult entity."""

    def test_no_match(self):
        """Test result with no match."""
        result = PatternMatchResult()
        assert not result.has_match
        assert result.best_pattern_name is None

    def test_with_match(self):
        """Test result with match."""
        pattern = DetectedPattern(
            pattern_type=PatternType.TOWER_LIKE,
            confidence=0.9,
        )
        result = PatternMatchResult(
            patterns=[pattern],
            best_match=pattern,
        )
        assert result.has_match
        assert result.best_pattern_name == "tower_like"


class TestFirewallResult:
    """Tests for FirewallResult entity."""

    def test_allow(self):
        """Test allow result."""
        result = FirewallResult.allow()
        assert result.allowed
        assert result.action == FirewallAction.ALLOW

    def test_block(self):
        """Test block result."""
        result = FirewallResult.block("Invalid operation")
        assert not result.allowed
        assert result.action == FirewallAction.BLOCK

    def test_auto_fix(self):
        """Test auto-fix result."""
        result = FirewallResult.auto_fix(
            message="Auto-fixed mode",
            pre_steps=[{"tool": "system_set_mode", "params": {"mode": "EDIT"}}],
        )
        assert result.allowed
        assert result.action == FirewallAction.AUTO_FIX
        assert result.needs_pre_steps

    def test_modify(self):
        """Test modify result."""
        result = FirewallResult.modify(
            message="Clamped parameter",
            modified_call={"tool": "mesh_bevel", "params": {"width": 0.5}},
        )
        assert result.allowed
        assert result.was_modified


class TestOverrideDecision:
    """Tests for OverrideDecision entity."""

    def test_no_override(self):
        """Test no override decision."""
        decision = OverrideDecision.no_override()
        assert not decision.should_override
        assert decision.replacement_count == 0

    def test_override_with_tools(self):
        """Test override with replacement tools."""
        tools = [
            ReplacementTool(tool_name="mesh_inset", params={"thickness": 0.03}),
            ReplacementTool(tool_name="mesh_extrude", params={"value": "$depth"}),
        ]
        reasons = [
            OverrideReason(
                rule_name="screen_cutout",
                description="Detected phone pattern",
            )
        ]
        decision = OverrideDecision.override_with_tools(tools, reasons)
        assert decision.should_override
        assert decision.replacement_count == 2

    def test_resolve_params_inheritance(self):
        """Test parameter inheritance in replacement tools."""
        tool = ReplacementTool(
            tool_name="mesh_extrude",
            params={"mode": "NORMAL"},
            inherit_params=["value"],
        )
        resolved = tool.resolve_params({"value": 1.5, "other": "x"})
        assert resolved == {"mode": "NORMAL", "value": 1.5}

    def test_resolve_params_dollar_syntax(self):
        """Test $param_name syntax resolution."""
        tool = ReplacementTool(
            tool_name="mesh_extrude",
            params={"value": "$depth"},
        )
        resolved = tool.resolve_params({"depth": 2.0})
        assert resolved == {"value": 2.0}

    def test_workflow_expansion(self):
        """Test workflow expansion decision."""
        tools = [
            ReplacementTool(tool_name="step1", params={}),
            ReplacementTool(tool_name="step2", params={}),
        ]
        decision = OverrideDecision.expand_to_workflow(
            workflow_name="phone_workflow",
            tools=tools,
            reason="Pattern matched phone_like",
        )
        assert decision.is_workflow_expansion
        assert decision.workflow_name == "phone_workflow"
