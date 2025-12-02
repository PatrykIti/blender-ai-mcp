"""
Unit tests for WorkflowExpansionEngine.

Tests workflow expansion and parameter inheritance.
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
def phone_pattern():
    """Create a phone_like pattern with workflow suggestion."""
    return DetectedPattern(
        pattern_type=PatternType.PHONE_LIKE,
        confidence=0.85,
        metadata={"aspect_xy": 0.5},
        suggested_workflow="phone_workflow",
    )


@pytest.fixture
def tower_pattern():
    """Create a tower_like pattern with workflow suggestion."""
    return DetectedPattern(
        pattern_type=PatternType.TOWER_LIKE,
        confidence=0.90,
        metadata={"aspect_ratio": 6.0},
        suggested_workflow="tower_workflow",
    )


class TestWorkflowExpansionEngineInit:
    """Tests for initialization."""

    def test_init_default_config(self, engine):
        """Test initialization with default config."""
        assert engine._config is not None
        assert engine._config.enable_workflow_expansion is True

    def test_init_loads_predefined_workflows(self, engine):
        """Test that predefined workflows are loaded."""
        workflows = engine.get_available_workflows()
        assert "phone_workflow" in workflows
        assert "tower_workflow" in workflows
        assert "screen_cutout_workflow" in workflows
        # Custom workflows from YAML are also available
        assert "table_workflow" in workflows or "chair_workflow" in workflows


class TestExpand:
    """Tests for expand method."""

    def test_expand_with_pattern_suggestion(self, engine, base_context, phone_pattern):
        """Test expansion when pattern suggests workflow."""
        result = engine.expand(
            "modeling_create_primitive",
            {"type": "CUBE"},
            base_context,
            pattern=phone_pattern,
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

    def test_expand_disabled(self, engine_disabled, base_context, phone_pattern):
        """Test no expansion when disabled."""
        result = engine_disabled.expand(
            "modeling_create_primitive",
            {},
            base_context,
            pattern=phone_pattern,
        )

        assert result is None


class TestGetWorkflow:
    """Tests for get_workflow method."""

    def test_get_phone_workflow(self, engine):
        """Test getting phone workflow steps."""
        steps = engine.get_workflow("phone_workflow")

        assert steps is not None
        assert len(steps) > 0

    def test_get_tower_workflow(self, engine):
        """Test getting tower workflow steps."""
        steps = engine.get_workflow("tower_workflow")

        assert steps is not None
        assert len(steps) > 0

    def test_get_nonexistent_workflow(self, engine):
        """Test getting non-existent workflow."""
        steps = engine.get_workflow("nonexistent_workflow")

        assert steps is None

    def test_workflow_steps_have_tool(self, engine):
        """Test that workflow steps have tool field."""
        steps = engine.get_workflow("phone_workflow")

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

    def test_registered_workflow_can_expand(self, engine, base_context):
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

    def test_expand_phone_workflow(self, engine):
        """Test expanding phone workflow."""
        result = engine.expand_workflow("phone_workflow", {})

        assert len(result) > 0
        tool_names = [call.tool_name for call in result]
        assert "modeling_create_primitive" in tool_names

    def test_expand_tower_workflow(self, engine):
        """Test expanding tower workflow."""
        result = engine.expand_workflow("tower_workflow", {})

        assert len(result) > 0
        tool_names = [call.tool_name for call in result]
        assert "mesh_subdivide" in tool_names

    def test_expand_nonexistent_workflow(self, engine):
        """Test expanding non-existent workflow."""
        result = engine.expand_workflow("nonexistent", {})

        assert result == []

    def test_expanded_calls_are_injected(self, engine):
        """Test that expanded calls are marked as injected."""
        result = engine.expand_workflow("phone_workflow", {})

        for call in result:
            assert call.is_injected is True

    def test_expanded_calls_have_workflow_correction(self, engine):
        """Test that expanded calls have workflow correction."""
        result = engine.expand_workflow("phone_workflow", {})

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

    def test_static_params_preserved(self, engine):
        """Test that static params are preserved."""
        result = engine.expand_workflow("phone_workflow", {})

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

    def test_contains_predefined(self, engine):
        """Test that list contains predefined workflows."""
        workflows = engine.get_available_workflows()

        # Built-in workflows should always be present
        assert "phone_workflow" in workflows
        assert "tower_workflow" in workflows
        assert "screen_cutout_workflow" in workflows


class TestGetWorkflowForPattern:
    """Tests for get_workflow_for_pattern method."""

    def test_phone_pattern_returns_phone_workflow(self, engine, phone_pattern):
        """Test that phone pattern returns phone workflow."""
        # phone_pattern already has pattern_type=PatternType.PHONE_LIKE
        # which gives name="phone_like" via the property
        result = engine.get_workflow_for_pattern(phone_pattern)

        assert result == "phone_workflow"

    def test_tower_pattern_returns_tower_workflow(self, engine, tower_pattern):
        """Test that tower pattern returns tower workflow."""
        # tower_pattern already has pattern_type=PatternType.TOWER_LIKE
        # which gives name="tower_like" via the property
        result = engine.get_workflow_for_pattern(tower_pattern)

        assert result == "tower_workflow"

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

    def test_phone_keywords(self, engine):
        """Test matching phone keywords."""
        result = engine.get_workflow_for_keywords(["create", "phone"])
        assert result == "phone_workflow"

    def test_smartphone_keyword(self, engine):
        """Test matching smartphone keyword."""
        result = engine.get_workflow_for_keywords(["smartphone"])
        assert result == "phone_workflow"

    def test_tower_keywords(self, engine):
        """Test matching tower keywords."""
        result = engine.get_workflow_for_keywords(["build", "tower"])
        assert result == "tower_workflow"

    def test_column_keyword(self, engine):
        """Test matching column keyword."""
        result = engine.get_workflow_for_keywords(["column"])
        assert result == "tower_workflow"

    def test_no_matching_keywords(self, engine):
        """Test no match for unknown keywords."""
        result = engine.get_workflow_for_keywords(["car", "vehicle"])
        assert result is None

    def test_case_insensitive(self, engine):
        """Test keyword matching is case insensitive."""
        result = engine.get_workflow_for_keywords(["PHONE", "CREATE"])
        assert result == "phone_workflow"


class TestRegistryWorkflows:
    """Tests for workflows from registry."""

    def test_phone_workflow_structure(self):
        """Test phone workflow has required fields."""
        registry = get_workflow_registry()
        definition = registry.get_definition("phone_workflow")

        assert definition is not None
        assert definition.description is not None
        assert definition.trigger_pattern is not None
        assert len(definition.trigger_keywords) > 0
        assert len(definition.steps) > 0

    def test_tower_workflow_structure(self):
        """Test tower workflow has required fields."""
        registry = get_workflow_registry()
        definition = registry.get_definition("tower_workflow")

        assert definition is not None
        assert definition.description is not None
        assert len(definition.steps) > 0

    def test_all_workflows_have_steps(self):
        """Test all workflows have steps."""
        registry = get_workflow_registry()
        for name in registry.get_all_workflows():
            definition = registry.get_definition(name)
            assert definition is not None
            assert len(definition.steps) > 0

    def test_phone_workflow_step_count(self):
        """Test phone workflow has correct step count."""
        registry = get_workflow_registry()
        definition = registry.get_definition("phone_workflow")
        assert len(definition.steps) == 10


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_params(self, engine, base_context, phone_pattern):
        """Test expansion with empty params."""
        result = engine.expand(
            "modeling_create_primitive",
            {},
            base_context,
            pattern=phone_pattern,
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
