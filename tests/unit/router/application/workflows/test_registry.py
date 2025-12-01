"""
Unit tests for WorkflowRegistry.

Tests for workflow registration, lookup, and expansion.
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
from server.router.application.workflows.phone_workflow import phone_workflow
from server.router.application.workflows.tower_workflow import tower_workflow
from server.router.domain.entities.tool_call import CorrectedToolCall


class TestWorkflowRegistry:
    """Tests for WorkflowRegistry."""

    @pytest.fixture
    def registry(self):
        """Create a fresh registry for testing."""
        return WorkflowRegistry()

    def test_builtin_workflows_registered(self, registry):
        """Test that built-in workflows are registered on init."""
        workflows = registry.get_all_workflows()
        assert "phone_workflow" in workflows
        assert "tower_workflow" in workflows
        assert "screen_cutout_workflow" in workflows

    def test_get_workflow(self, registry):
        """Test getting a workflow by name."""
        workflow = registry.get_workflow("phone_workflow")
        assert workflow is not None
        assert workflow.name == "phone_workflow"

    def test_get_workflow_not_found(self, registry):
        """Test getting non-existent workflow returns None."""
        workflow = registry.get_workflow("nonexistent")
        assert workflow is None

    def test_get_definition(self, registry):
        """Test getting workflow definition."""
        definition = registry.get_definition("phone_workflow")
        assert definition is not None
        assert isinstance(definition, WorkflowDefinition)
        assert definition.name == "phone_workflow"

    def test_find_by_pattern_phone(self, registry):
        """Test finding workflow by phone pattern."""
        name = registry.find_by_pattern("phone_like")
        assert name is not None
        assert name in ["phone_workflow", "screen_cutout_workflow"]

    def test_find_by_pattern_tower(self, registry):
        """Test finding workflow by tower pattern."""
        name = registry.find_by_pattern("tower_like")
        assert name == "tower_workflow"

    def test_find_by_pattern_unknown(self, registry):
        """Test finding workflow by unknown pattern returns None."""
        name = registry.find_by_pattern("unknown_pattern")
        assert name is None

    def test_find_by_keywords_phone(self, registry):
        """Test finding workflow by phone keywords."""
        name = registry.find_by_keywords("create a smartphone")
        assert name == "phone_workflow"

    def test_find_by_keywords_tower(self, registry):
        """Test finding workflow by tower keywords."""
        name = registry.find_by_keywords("build tall tower")
        assert name == "tower_workflow"

    def test_find_by_keywords_screen(self, registry):
        """Test finding workflow by screen keywords."""
        name = registry.find_by_keywords("add display cutout")
        assert name == "screen_cutout_workflow"

    def test_find_by_keywords_no_match(self, registry):
        """Test finding workflow by keywords with no match."""
        name = registry.find_by_keywords("something completely different")
        assert name is None

    def test_expand_workflow_phone(self, registry):
        """Test expanding phone workflow."""
        calls = registry.expand_workflow("phone_workflow")
        assert len(calls) == 10
        assert all(isinstance(c, CorrectedToolCall) for c in calls)

        # Check first step is create primitive
        assert calls[0].tool_name == "modeling_create_primitive"
        assert calls[0].is_injected is True

    def test_expand_workflow_with_params(self, registry):
        """Test expanding workflow with custom parameters."""
        calls = registry.expand_workflow("tower_workflow", {"height": 5.0})

        # Find the transform step
        transform_call = next(c for c in calls if c.tool_name == "modeling_transform_object")
        assert transform_call.params["scale"][2] == 5.0

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

    def test_expand_custom_definition(self, registry):
        """Test expanding a custom definition."""
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

    def test_workflow_info_builtin(self, registry):
        """Test getting workflow info for built-in workflow."""
        info = registry.get_workflow_info("phone_workflow")

        assert info is not None
        assert info["name"] == "phone_workflow"
        assert info["type"] == "builtin"
        assert "trigger_pattern" in info
        assert "step_count" in info
        assert info["step_count"] == 10

    def test_workflow_info_nonexistent(self, registry):
        """Test getting workflow info for non-existent workflow."""
        info = registry.get_workflow_info("nonexistent")
        assert info is None

    def test_get_all_workflows_sorted(self, registry):
        """Test get_all_workflows returns sorted list."""
        workflows = registry.get_all_workflows()
        assert workflows == sorted(workflows)


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
        # Note: Due to module-level singleton, these should be same instance
        assert registry1 is registry2
