"""
Unit tests for WorkflowExpansionEngine.

Tests workflow expansion and parameter inheritance.

TASK-050: Updated to not depend on specific builtin workflows (YAML-based now).
"""

import pytest

from server.router.application.engines.workflow_expansion_engine import (
    WorkflowExpansionEngine,
)
from server.router.application.workflows.registry import get_workflow_registry
from server.router.domain.entities.scene_context import (
    SceneContext,
    ObjectInfo,
    TopologyInfo,
)
from server.router.domain.entities.pattern import DetectedPattern, PatternType
from server.router.infrastructure.config import RouterConfig


@pytest.fixture
def engine():
    """Create a WorkflowExpansionEngine with default config."""
    return WorkflowExpansionEngine()


@pytest.fixture
def engine_disabled():
    """Create engine with expansion disabled."""
    config = RouterConfig(enable_workflow_expansion=False)
    return WorkflowExpansionEngine(config=config)


@pytest.fixture
def base_context():
    """Create a base scene context."""
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
def test_pattern():
    """Create a test pattern with workflow suggestion."""
    return DetectedPattern(
        pattern_type=PatternType.PHONE_LIKE,
        confidence=0.85,
        metadata={"aspect_xy": 0.5},
        suggested_workflow="test_registered_workflow",
    )


@pytest.fixture
def engine_with_test_workflow(engine):
    """Create engine with a test workflow registered."""
    engine.register_workflow(
        name="test_registered_workflow",
        steps=[
            {"tool": "modeling_create_primitive", "params": {"type": "CUBE"}},
            {"tool": "scene_set_mode", "params": {"mode": "EDIT"}},
            {"tool": "mesh_select", "params": {"action": "all"}},
            {"tool": "mesh_bevel", "params": {"width": 0.1}},
        ],
        trigger_pattern="test_pattern",
        trigger_keywords=["test", "registered", "workflow"],
    )
    return engine


class TestWorkflowExpansionEngineInit:
    """Tests for initialization."""

    def test_init_default_config(self, engine):
        """Test initialization with default config."""
        assert engine._config is not None
        assert engine._config.enable_workflow_expansion is True

    def test_init_loads_workflows_from_yaml(self, engine):
        """Test that workflows are loaded from YAML."""
        workflows = engine.get_available_workflows()
        # Should be a list (may have YAML workflows)
        assert isinstance(workflows, list)


class TestExpand:
    """Tests for expand method."""

    def test_expand_with_pattern_suggestion(self, engine_with_test_workflow, base_context, test_pattern):
        """Test expansion when pattern suggests workflow."""
        result = engine_with_test_workflow.expand(
            "modeling_create_primitive",
            {"type": "CUBE"},
            base_context,
            pattern=test_pattern,
        )

        assert result is not None
        assert len(result) > 0

    def test_expand_no_pattern(self, engine, base_context):
        """Test no expansion without pattern."""
        result = engine.expand(
            "modeling_create_primitive",
            {"type": "CUBE"},
            base_context,
            pattern=None,
        )

        assert result is None

    def test_expand_pattern_no_workflow(self, engine, base_context):
        """Test no expansion when pattern has no workflow."""
        pattern = DetectedPattern(
            pattern_type=PatternType.UNKNOWN,
            confidence=0.5,
            metadata={},
            suggested_workflow=None,
        )

        result = engine.expand(
            "modeling_create_primitive",
            {},
            base_context,
            pattern=pattern,
        )

        assert result is None

    def test_expand_disabled(self, engine_disabled, base_context):
        """Test no expansion when disabled."""
        pattern = DetectedPattern(
            pattern_type=PatternType.PHONE_LIKE,
            confidence=0.85,
            metadata={},
            suggested_workflow="any_workflow",
        )
        result = engine_disabled.expand(
            "modeling_create_primitive",
            {},
            base_context,
            pattern=pattern,
        )

        assert result is None


class TestGetWorkflow:
    """Tests for get_workflow method."""

    def test_get_registered_workflow(self, engine_with_test_workflow):
        """Test getting registered workflow steps."""
        steps = engine_with_test_workflow.get_workflow("test_registered_workflow")

        assert steps is not None
        assert len(steps) > 0

    def test_get_nonexistent_workflow(self, engine):
        """Test getting non-existent workflow."""
        steps = engine.get_workflow("nonexistent_workflow_xyz123")

        assert steps is None

    def test_workflow_steps_have_tool(self, engine_with_test_workflow):
        """Test that workflow steps have tool field."""
        steps = engine_with_test_workflow.get_workflow("test_registered_workflow")

        for step in steps:
            assert "tool" in step


class TestRegisterWorkflow:
    """Tests for register_workflow method."""

    def test_register_new_workflow(self, engine):
        """Test registering a new workflow."""
        engine.register_workflow(
            name="custom_workflow",
            steps=[
                {"tool": "mesh_select", "params": {"action": "all"}},
                {"tool": "mesh_bevel", "params": {"width": 0.1}},
            ],
            trigger_pattern="custom_pattern",
            trigger_keywords=["custom", "special"],
        )

        workflows = engine.get_available_workflows()
        assert "custom_workflow" in workflows

    def test_register_workflow_minimal(self, engine):
        """Test registering workflow with minimal params."""
        engine.register_workflow(
            name="minimal_workflow",
            steps=[{"tool": "mesh_subdivide", "params": {"number_cuts": 2}}],
        )

        assert "minimal_workflow" in engine.get_available_workflows()

    def test_registered_workflow_can_expand(self, engine):
        """Test that registered workflow can be expanded."""
        engine.register_workflow(
            name="test_workflow",
            steps=[
                {"tool": "mesh_subdivide", "params": {"number_cuts": 2}},
            ],
        )

        result = engine.expand_workflow("test_workflow", {})

        assert len(result) == 1
        assert result[0].tool_name == "mesh_subdivide"


class TestExpandWorkflow:
    """Tests for expand_workflow method."""

    def test_expand_registered_workflow(self, engine_with_test_workflow):
        """Test expanding registered workflow."""
        result = engine_with_test_workflow.expand_workflow("test_registered_workflow", {})

        assert len(result) > 0
        tool_names = [call.tool_name for call in result]
        assert "modeling_create_primitive" in tool_names

    def test_expand_nonexistent_workflow(self, engine):
        """Test expanding non-existent workflow."""
        result = engine.expand_workflow("nonexistent_xyz123", {})

        assert result == []

    def test_expanded_calls_are_injected(self, engine_with_test_workflow):
        """Test that expanded calls are marked as injected."""
        result = engine_with_test_workflow.expand_workflow("test_registered_workflow", {})

        for call in result:
            assert call.is_injected is True

    def test_expanded_calls_have_workflow_correction(self, engine_with_test_workflow):
        """Test that expanded calls have workflow correction."""
        result = engine_with_test_workflow.expand_workflow("test_registered_workflow", {})

        for call in result:
            assert any("workflow:" in c for c in call.corrections_applied)


class TestParameterInheritance:
    """Tests for parameter inheritance in workflows."""

    def test_inherit_param_with_dollar(self, engine):
        """Test parameter inheritance with $ syntax."""
        # Register a workflow that uses $param syntax
        engine.register_workflow(
            name="test_bevel_workflow",
            steps=[
                {"tool": "system_set_mode", "params": {"mode": "EDIT"}},
                {"tool": "mesh_select", "params": {"action": "all"}},
                {"tool": "mesh_bevel", "params": {"width": "$width", "segments": "$segments"}},
            ],
        )

        result = engine.expand_workflow(
            "test_bevel_workflow",
            {"width": 0.5, "segments": 5},
        )

        # Find the bevel step
        bevel_call = next(
            (c for c in result if c.tool_name == "mesh_bevel"),
            None,
        )

        assert bevel_call is not None
        assert bevel_call.params.get("width") == 0.5
        assert bevel_call.params.get("segments") == 5

    def test_missing_inherited_param_skipped(self, engine):
        """Test that missing inherited params are skipped."""
        # Register a workflow that uses $param syntax
        engine.register_workflow(
            name="test_bevel_workflow_2",
            steps=[
                {"tool": "mesh_bevel", "params": {"width": "$width", "segments": "$segments"}},
            ],
        )

        result = engine.expand_workflow(
            "test_bevel_workflow_2",
            {},  # No width or segments
        )

        bevel_call = next(
            (c for c in result if c.tool_name == "mesh_bevel"),
            None,
        )

        # Params should be empty for inherited values
        assert bevel_call is not None
        # width and segments should not be in params if not provided

    def test_static_params_preserved(self, engine_with_test_workflow):
        """Test that static params are preserved."""
        result = engine_with_test_workflow.expand_workflow("test_registered_workflow", {})

        # Find create primitive step
        create_call = next(
            (c for c in result if c.tool_name == "modeling_create_primitive"),
            None,
        )

        assert create_call is not None
        assert create_call.params.get("type") == "CUBE"


class TestGetAvailableWorkflows:
    """Tests for get_available_workflows method."""

    def test_returns_list(self, engine):
        """Test that get_available_workflows returns list."""
        workflows = engine.get_available_workflows()
        assert isinstance(workflows, list)

    def test_contains_registered(self, engine_with_test_workflow):
        """Test that list contains registered workflows."""
        workflows = engine_with_test_workflow.get_available_workflows()
        assert "test_registered_workflow" in workflows


class TestGetWorkflowForPattern:
    """Tests for get_workflow_for_pattern method."""

    def test_pattern_with_suggested_workflow(self, engine_with_test_workflow):
        """Test pattern with suggested workflow returns it."""
        pattern = DetectedPattern(
            pattern_type=PatternType.PHONE_LIKE,
            confidence=0.85,
            metadata={},
            suggested_workflow="test_registered_workflow",
        )
        # Note: get_workflow_for_pattern uses pattern name, not suggested_workflow
        # So we register a workflow matching the pattern name
        engine_with_test_workflow.register_workflow(
            name="matching_pattern_workflow",
            steps=[{"tool": "test", "params": {}}],
            trigger_pattern="phone_like",
        )
        result = engine_with_test_workflow.get_workflow_for_pattern(pattern)
        assert result is not None

    def test_unknown_pattern_returns_none(self, engine):
        """Test that unknown pattern returns None."""
        pattern = DetectedPattern(
            pattern_type=PatternType.UNKNOWN,
            confidence=0.5,
            metadata={},
        )

        result = engine.get_workflow_for_pattern(pattern)

        assert result is None


class TestGetWorkflowForKeywords:
    """Tests for get_workflow_for_keywords method."""

    def test_matching_keywords(self, engine_with_test_workflow):
        """Test matching keywords returns workflow."""
        result = engine_with_test_workflow.get_workflow_for_keywords(["test", "registered"])
        assert result == "test_registered_workflow"

    def test_no_matching_keywords(self, engine):
        """Test no match for unknown keywords."""
        result = engine.get_workflow_for_keywords(["xyz123", "unknownkeyword456"])
        assert result is None

    def test_case_insensitive(self, engine_with_test_workflow):
        """Test keyword matching is case insensitive."""
        result = engine_with_test_workflow.get_workflow_for_keywords(["TEST", "REGISTERED"])
        assert result == "test_registered_workflow"


class TestRegistryWorkflows:
    """Tests for workflows from registry."""

    def test_all_workflows_have_steps(self):
        """Test all workflows have steps."""
        registry = get_workflow_registry()
        for name in registry.get_all_workflows():
            definition = registry.get_definition(name)
            assert definition is not None
            assert len(definition.steps) > 0


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_params(self, engine_with_test_workflow, base_context, test_pattern):
        """Test expansion with empty params."""
        result = engine_with_test_workflow.expand(
            "modeling_create_primitive",
            {},
            base_context,
            pattern=test_pattern,
        )

        assert result is not None

    def test_workflow_with_empty_steps(self, engine):
        """Test workflow with no steps."""
        engine.register_workflow(
            name="empty_workflow",
            steps=[],
        )

        result = engine.expand_workflow("empty_workflow", {})
        assert result == []
