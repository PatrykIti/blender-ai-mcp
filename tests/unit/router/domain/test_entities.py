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
    # Ensemble (TASK-053)
    MatcherResult,
    ModifierResult,
    EnsembleResult,
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


class TestMatcherResult:
    """Tests for MatcherResult entity (TASK-053-1)."""

    def test_create_basic(self):
        """Test basic creation."""
        result = MatcherResult(
            matcher_name="keyword",
            workflow_name="picnic_table_workflow",
            confidence=1.0,
            weight=0.40,
        )
        assert result.matcher_name == "keyword"
        assert result.workflow_name == "picnic_table_workflow"
        assert result.confidence == 1.0
        assert result.weight == 0.40

    def test_create_no_match(self):
        """Test creation with no match."""
        result = MatcherResult(
            matcher_name="semantic",
            workflow_name=None,
            confidence=0.0,
            weight=0.40,
        )
        assert result.workflow_name is None
        assert result.confidence == 0.0

    def test_weighted_score(self):
        """Test weighted score calculation."""
        result = MatcherResult(
            matcher_name="semantic",
            workflow_name="table_workflow",
            confidence=0.84,
            weight=0.40,
        )
        assert result.weighted_score == pytest.approx(0.336, rel=1e-3)

    def test_confidence_validation(self):
        """Test confidence value validation."""
        with pytest.raises(ValueError, match="Confidence must be between"):
            MatcherResult(
                matcher_name="test",
                workflow_name="test",
                confidence=1.5,  # Invalid
                weight=0.5,
            )

    def test_weight_validation(self):
        """Test weight value validation."""
        with pytest.raises(ValueError, match="Weight must be between"):
            MatcherResult(
                matcher_name="test",
                workflow_name="test",
                confidence=0.5,
                weight=1.5,  # Invalid
            )

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = MatcherResult(
            matcher_name="pattern",
            workflow_name="tower_workflow",
            confidence=0.95,
            weight=0.15,
            metadata={"pattern": "tower_like"},
        )
        data = result.to_dict()
        assert data["matcher_name"] == "pattern"
        assert data["workflow_name"] == "tower_workflow"
        assert data["confidence"] == 0.95
        assert data["weighted_score"] == pytest.approx(0.1425, rel=1e-3)
        assert data["metadata"]["pattern"] == "tower_like"


class TestModifierResult:
    """Tests for ModifierResult entity (TASK-053-1)."""

    def test_create_with_modifiers(self):
        """Test creation with modifiers."""
        result = ModifierResult(
            modifiers={"leg_angle_left": 0, "leg_angle_right": 0},
            matched_keywords=["prosty", "proste nogi"],
            confidence_map={"prosty": 1.0, "proste nogi": 1.0},
        )
        assert result.modifiers["leg_angle_left"] == 0
        assert len(result.matched_keywords) == 2
        assert result.has_modifiers()

    def test_create_empty(self):
        """Test creation with no modifiers."""
        result = ModifierResult(
            modifiers={},
            matched_keywords=[],
            confidence_map={},
        )
        assert not result.has_modifiers()
        assert len(result.matched_keywords) == 0

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = ModifierResult(
            modifiers={"leg_angle_left": 0},
            matched_keywords=["prosty"],
            confidence_map={"prosty": 1.0},
        )
        data = result.to_dict()
        assert data["modifiers"]["leg_angle_left"] == 0
        assert data["matched_keywords"] == ["prosty"]
        assert data["has_modifiers"] is True


class TestEnsembleResult:
    """Tests for EnsembleResult entity (TASK-053-1)."""

    def test_create_basic(self):
        """Test basic creation."""
        result = EnsembleResult(
            workflow_name="picnic_table_workflow",
            final_score=0.768,
            confidence_level="HIGH",
            modifiers={"leg_angle_left": 0, "leg_angle_right": 0},
            matcher_contributions={"keyword": 0.0, "semantic": 0.336, "pattern": 0.0},
            requires_adaptation=False,
        )
        assert result.workflow_name == "picnic_table_workflow"
        assert result.final_score == 0.768
        assert result.confidence_level == "HIGH"
        assert result.is_match()

    def test_create_no_match(self):
        """Test creation with no match."""
        result = EnsembleResult(
            workflow_name=None,
            final_score=0.0,
            confidence_level="NONE",
            modifiers={},
            matcher_contributions={},
            requires_adaptation=False,
        )
        assert not result.is_match()
        assert result.confidence_level == "NONE"

    def test_confidence_alias(self):
        """Test confidence property (backward compatibility)."""
        result = EnsembleResult(
            workflow_name="test_workflow",
            final_score=0.85,
            confidence_level="HIGH",
            modifiers={},
            matcher_contributions={"semantic": 0.34},
            requires_adaptation=False,
        )
        # Backward compatibility with MatchResult.confidence
        assert result.confidence == result.final_score
        assert result.confidence == 0.85

    def test_needs_adaptation(self):
        """Test needs_adaptation logic."""
        # HIGH confidence - no adaptation needed
        result_high = EnsembleResult(
            workflow_name="test",
            final_score=0.8,
            confidence_level="HIGH",
            modifiers={},
            matcher_contributions={},
            requires_adaptation=True,
        )
        assert not result_high.needs_adaptation()

        # MEDIUM confidence - adaptation needed
        result_medium = EnsembleResult(
            workflow_name="test",
            final_score=0.5,
            confidence_level="MEDIUM",
            modifiers={},
            matcher_contributions={},
            requires_adaptation=True,
        )
        assert result_medium.needs_adaptation()

    def test_composition_mode(self):
        """Test composition mode."""
        result = EnsembleResult(
            workflow_name="table_workflow",
            final_score=0.75,
            confidence_level="HIGH",
            modifiers={},
            matcher_contributions={"semantic": 0.3, "keyword": 0.4},
            requires_adaptation=False,
            composition_mode=True,
            extra_workflows=["chair_workflow"],
        )
        assert result.composition_mode
        assert len(result.extra_workflows) == 1
        assert result.extra_workflows[0] == "chair_workflow"

    def test_confidence_level_validation(self):
        """Test confidence level validation."""
        with pytest.raises(ValueError, match="Confidence level must be one of"):
            EnsembleResult(
                workflow_name="test",
                final_score=0.5,
                confidence_level="INVALID",  # Invalid level
                modifiers={},
                matcher_contributions={},
                requires_adaptation=False,
            )

    def test_final_score_validation(self):
        """Test final score validation."""
        with pytest.raises(ValueError, match="Final score must be"):
            EnsembleResult(
                workflow_name="test",
                final_score=-0.1,  # Invalid negative score
                confidence_level="LOW",
                modifiers={},
                matcher_contributions={},
                requires_adaptation=False,
            )

    def test_has_modifiers(self):
        """Test has_modifiers check."""
        result_with = EnsembleResult(
            workflow_name="test",
            final_score=0.5,
            confidence_level="MEDIUM",
            modifiers={"angle": 0},
            matcher_contributions={},
            requires_adaptation=False,
        )
        assert result_with.has_modifiers()

        result_without = EnsembleResult(
            workflow_name="test",
            final_score=0.5,
            confidence_level="MEDIUM",
            modifiers={},
            matcher_contributions={},
            requires_adaptation=False,
        )
        assert not result_without.has_modifiers()

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = EnsembleResult(
            workflow_name="picnic_table_workflow",
            final_score=0.768,
            confidence_level="HIGH",
            modifiers={"leg_angle_left": 0},
            matcher_contributions={"semantic": 0.336},
            requires_adaptation=False,
            composition_mode=False,
            extra_workflows=[],
        )
        data = result.to_dict()
        assert data["workflow_name"] == "picnic_table_workflow"
        assert data["final_score"] == 0.768
        assert data["confidence_level"] == "HIGH"
        assert data["modifiers"]["leg_angle_left"] == 0
        assert data["has_modifiers"] is True
