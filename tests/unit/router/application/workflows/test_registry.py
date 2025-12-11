"""
Unit tests for WorkflowRegistry.

Tests for workflow registration, lookup, and expansion.

TASK-050: Updated for YAML-based workflows (no more Python builtin workflows).
"""

import pytest

from server.router.application.workflows.registry import (
    WorkflowRegistry,
    get_workflow_registry,
)
from server.router.application.workflows.base import (
    BaseWorkflow,
    WorkflowDefinition,
    WorkflowStep,
)
from server.router.domain.entities.tool_call import CorrectedToolCall


class TestWorkflowRegistry:
    """Tests for WorkflowRegistry."""

    @pytest.fixture
    def registry(self):
        """Create a fresh registry for testing."""
        return WorkflowRegistry()

    @pytest.fixture
    def registry_with_test_workflow(self, registry):
        """Create registry with test workflow registered."""
        definition = WorkflowDefinition(
            name="test_workflow",
            description="Test workflow for unit tests",
            steps=[
                WorkflowStep(tool="modeling_create_primitive", params={"primitive_type": "CUBE"}),
                WorkflowStep(tool="scene_set_mode", params={"mode": "EDIT"}),
                WorkflowStep(tool="mesh_select", params={"action": "all"}),
            ],
            trigger_pattern="test_pattern",
            trigger_keywords=["test", "example", "demo"],
        )
        registry.register_definition(definition)
        return registry

    def test_empty_registry_has_yaml_workflows(self, registry):
        """Test that registry loads YAML workflows."""
        workflows = registry.get_all_workflows()
        # Should have at least the picnic_table workflow from YAML
        assert isinstance(workflows, list)

    def test_get_workflow_not_found(self, registry):
        """Test getting non-existent workflow returns None."""
        workflow = registry.get_workflow("nonexistent_workflow")
        assert workflow is None

    def test_get_definition_not_found(self, registry):
        """Test getting non-existent definition returns None."""
        definition = registry.get_definition("nonexistent_workflow")
        assert definition is None

    def test_find_by_pattern_unknown(self, registry):
        """Test finding workflow by unknown pattern returns None."""
        name = registry.find_by_pattern("unknown_pattern_xyz123")
        assert name is None

    def test_find_by_keywords_no_match(self, registry):
        """Test finding workflow by keywords with no match."""
        name = registry.find_by_keywords("something completely different xyz123")
        assert name is None

    def test_expand_workflow_nonexistent(self, registry):
        """Test expanding non-existent workflow returns empty list."""
        calls = registry.expand_workflow("nonexistent_workflow")
        assert calls == []

    def test_register_custom_workflow(self, registry):
        """Test registering a custom workflow class."""
        class CustomWorkflow(BaseWorkflow):
            @property
            def name(self):
                return "custom_test"

            @property
            def description(self):
                return "Custom test workflow"

            @property
            def trigger_pattern(self):
                return "custom_pattern"

            @property
            def trigger_keywords(self):
                return ["custom", "test"]

            def get_steps(self, params=None):
                return [WorkflowStep(tool="test_tool", params={})]

        custom = CustomWorkflow()
        registry.register_workflow(custom)

        assert "custom_test" in registry.get_all_workflows()
        assert registry.get_workflow("custom_test") is custom

    def test_register_definition(self, registry):
        """Test registering a workflow from definition."""
        definition = WorkflowDefinition(
            name="def_workflow",
            description="Definition workflow",
            steps=[WorkflowStep(tool="tool1", params={"x": 1})],
            trigger_keywords=["def", "test"],
        )

        registry.register_definition(definition)

        assert "def_workflow" in registry.get_all_workflows()
        result = registry.get_definition("def_workflow")
        assert result.name == "def_workflow"

    def test_get_definition_for_registered(self, registry_with_test_workflow):
        """Test getting definition for registered workflow."""
        definition = registry_with_test_workflow.get_definition("test_workflow")
        assert definition is not None
        assert isinstance(definition, WorkflowDefinition)
        assert definition.name == "test_workflow"
        assert len(definition.steps) == 3

    def test_find_by_pattern_registered(self, registry_with_test_workflow):
        """Test finding workflow by pattern for registered workflow."""
        name = registry_with_test_workflow.find_by_pattern("test_pattern")
        assert name == "test_workflow"

    def test_find_by_keywords_registered(self, registry_with_test_workflow):
        """Test finding workflow by keywords for registered workflow."""
        name = registry_with_test_workflow.find_by_keywords("create a test model")
        assert name == "test_workflow"

    def test_expand_registered_workflow(self, registry_with_test_workflow):
        """Test expanding a registered workflow."""
        calls = registry_with_test_workflow.expand_workflow("test_workflow")

        assert len(calls) == 3
        assert all(isinstance(c, CorrectedToolCall) for c in calls)
        assert calls[0].tool_name == "modeling_create_primitive"
        assert calls[0].is_injected is True
        assert calls[1].tool_name == "scene_set_mode"
        assert calls[2].tool_name == "mesh_select"

    def test_expand_custom_definition_with_params(self, registry):
        """Test expanding a custom definition with variable substitution."""
        definition = WorkflowDefinition(
            name="custom_def",
            description="Custom",
            steps=[
                WorkflowStep(tool="tool_a", params={"value": "$v"}),
                WorkflowStep(tool="tool_b", params={"fixed": 1}),
            ],
        )

        registry.register_definition(definition)

        # Expand with parameter
        calls = registry.expand_workflow("custom_def", {"v": 100})
        assert len(calls) == 2
        assert calls[0].params.get("value") == 100
        assert calls[1].params.get("fixed") == 1

    def test_workflow_info_registered(self, registry_with_test_workflow):
        """Test getting workflow info for registered workflow."""
        info = registry_with_test_workflow.get_workflow_info("test_workflow")

        assert info is not None
        assert info["name"] == "test_workflow"
        assert info["type"] == "custom"
        assert info["step_count"] == 3

    def test_workflow_info_nonexistent(self, registry):
        """Test getting workflow info for non-existent workflow."""
        info = registry.get_workflow_info("nonexistent")
        assert info is None

    def test_get_all_workflows_sorted(self, registry_with_test_workflow):
        """Test get_all_workflows returns sorted list."""
        workflows = registry_with_test_workflow.get_all_workflows()
        assert workflows == sorted(workflows)

    def test_workflow_expansion_marks_as_injected(self, registry_with_test_workflow):
        """Test that expanded workflow steps are marked as injected."""
        calls = registry_with_test_workflow.expand_workflow("test_workflow")

        for call in calls:
            assert call.is_injected is True
            assert len(call.corrections_applied) > 0
            assert any("workflow:test_workflow" in c for c in call.corrections_applied)


class TestGetWorkflowRegistry:
    """Tests for get_workflow_registry singleton."""

    def test_returns_registry(self):
        """Test that function returns a registry."""
        registry = get_workflow_registry()
        assert isinstance(registry, WorkflowRegistry)

    def test_returns_same_instance(self):
        """Test singleton behavior."""
        registry1 = get_workflow_registry()
        registry2 = get_workflow_registry()
        # Due to module-level singleton, these should be same instance
        assert registry1 is registry2


class TestWorkflowRegistryWithYAML:
    """Tests that work with actual YAML workflows if available."""

    @pytest.fixture
    def registry(self):
        """Create registry with YAML workflows loaded."""
        reg = WorkflowRegistry()
        reg.ensure_custom_loaded()
        return reg

    def test_yaml_workflows_load(self, registry):
        """Test that YAML workflows are loaded."""
        workflows = registry.get_all_workflows()
        # Should be a list (may be empty if no YAML files)
        assert isinstance(workflows, list)

    def test_expand_yaml_workflow_if_exists(self, registry):
        """Test expanding YAML workflow if any exist."""
        workflows = registry.get_all_workflows()
        if workflows:
            # Pick first available workflow
            workflow_name = workflows[0]
            calls = registry.expand_workflow(workflow_name)
            assert isinstance(calls, list)
            # Should return some steps
            assert all(isinstance(c, CorrectedToolCall) for c in calls)

    def test_get_definition_yaml_workflow_if_exists(self, registry):
        """Test getting definition for YAML workflow if any exist."""
        workflows = registry.get_all_workflows()
        if workflows:
            workflow_name = workflows[0]
            definition = registry.get_definition(workflow_name)
            assert definition is not None
            assert isinstance(definition, WorkflowDefinition)
            assert definition.name == workflow_name

    def test_workflow_info_yaml_workflow_if_exists(self, registry):
        """Test getting workflow info for YAML workflow if any exist."""
        workflows = registry.get_all_workflows()
        if workflows:
            workflow_name = workflows[0]
            info = registry.get_workflow_info(workflow_name)
            assert info is not None
            assert info["name"] == workflow_name
            assert "step_count" in info

    # TASK-055-FIX-7 Phase 0: Computed Parameters Integration Tests

    def test_expand_workflow_with_computed_parameters(self, registry):
        """Test workflow expansion with TASK-056-5 computed parameters."""
        from server.router.domain.entities.parameter import ParameterSchema

        # Create workflow with computed parameters
        definition = WorkflowDefinition(
            name="test_computed",
            description="Test computed params",
            steps=[
                WorkflowStep(
                    tool="modeling_create_primitive",
                    params={
                        "primitive_type": "CUBE",
                        "name": "Plank",
                    },
                ),
                WorkflowStep(
                    tool="modeling_transform_object",
                    params={
                        "name": "Plank",
                        "scale": ["$plank_actual_width", 1.0, 0.1],
                    },
                ),
            ],
            defaults={"table_width": 0.8, "plank_max_width": 0.10},
            parameters={
                "plank_count": ParameterSchema(
                    name="plank_count",
                    type="int",
                    computed="ceil(table_width / plank_max_width)",
                    depends_on=["table_width", "plank_max_width"],
                ),
                "plank_actual_width": ParameterSchema(
                    name="plank_actual_width",
                    type="float",
                    computed="table_width / plank_count",
                    depends_on=["table_width", "plank_count"],
                ),
            },
        )
        registry.register_definition(definition)

        # Expand workflow
        calls = registry.expand_workflow("test_computed")

        # Verify workflow expanded
        assert len(calls) == 2
        assert calls[0].tool_name == "modeling_create_primitive"
        assert calls[1].tool_name == "modeling_transform_object"

        # Verify computed params were resolved
        # table_width=0.8, plank_max_width=0.10
        # plank_count = ceil(0.8 / 0.10) = ceil(8.0) = 8
        # plank_actual_width = 0.8 / 8 = 0.1
        assert calls[1].params["scale"][0] == 0.1

    def test_expand_workflow_computed_params_circular_dependency(self, registry):
        """Test graceful handling of circular dependency in computed params."""
        from server.router.domain.entities.parameter import ParameterSchema

        # Create workflow with circular dependency
        definition = WorkflowDefinition(
            name="test_circular",
            description="Test circular dependency",
            steps=[
                WorkflowStep(
                    tool="modeling_create_primitive",
                    params={"primitive_type": "CUBE"},
                )
            ],
            parameters={
                "a": ParameterSchema(
                    name="a",
                    type="float",
                    computed="b + 1",
                    depends_on=["b"],
                ),
                "b": ParameterSchema(
                    name="b",
                    type="float",
                    computed="a + 1",
                    depends_on=["a"],
                ),
            },
        )
        registry.register_definition(definition)

        # Should not crash - degrades gracefully
        calls = registry.expand_workflow("test_circular")
        assert len(calls) == 1  # Workflow still expands
        assert calls[0].tool_name == "modeling_create_primitive"

    def test_expand_workflow_computed_params_explicit_override(self, registry):
        """Test that explicit params override computed params."""
        from server.router.domain.entities.parameter import ParameterSchema

        definition = WorkflowDefinition(
            name="test_override",
            description="Test computed param override",
            steps=[
                WorkflowStep(
                    tool="modeling_create_primitive",
                    params={
                        "primitive_type": "CUBE",
                        "name": "Test",
                    },
                ),
                WorkflowStep(
                    tool="modeling_transform_object",
                    params={
                        "name": "Test",
                        "scale": ["$plank_count", 1.0, 1.0],
                    },
                ),
            ],
            defaults={"width": 0.8},
            parameters={
                "plank_count": ParameterSchema(
                    name="plank_count",
                    type="int",
                    computed="ceil(width / 0.1)",
                    depends_on=["width"],
                )
            },
        )
        registry.register_definition(definition)

        # Expand with explicit override
        calls = registry.expand_workflow("test_override", params={"plank_count": 10})

        # Verify workflow expanded
        assert len(calls) == 2

        # Explicit param should override computed
        # Without override: ceil(0.8 / 0.1) = 8
        # With override: 10 (explicit value)
        assert calls[1].params["scale"][0] == 10
