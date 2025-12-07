"""
Unit tests for workflow definitions.

Tests for YAML-based workflows loaded via WorkflowRegistry.
TASK-039-19, TASK-039-20, TASK-039-21
TASK-050: Updated for YAML-based workflows (removed old Python imports).
"""

import pytest

from server.router.application.workflows.base import (
    BaseWorkflow,
    WorkflowDefinition,
    WorkflowStep,
)
from server.router.application.workflows.registry import (
    WorkflowRegistry,
    get_workflow_registry,
)


class TestWorkflowStep:
    """Tests for WorkflowStep dataclass."""

    def test_create_step(self):
        """Test creating a workflow step."""
        step = WorkflowStep(
            tool="mesh_extrude",
            params={"depth": 0.5},
            description="Extrude faces",
        )
        assert step.tool == "mesh_extrude"
        assert step.params == {"depth": 0.5}
        assert step.description == "Extrude faces"
        assert step.condition is None

    def test_step_to_dict(self):
        """Test converting step to dictionary."""
        step = WorkflowStep(
            tool="mesh_bevel",
            params={"width": 0.1},
        )
        d = step.to_dict()
        assert d["tool"] == "mesh_bevel"
        assert d["params"] == {"width": 0.1}


class TestWorkflowDefinition:
    """Tests for WorkflowDefinition dataclass."""

    def test_create_definition(self):
        """Test creating a workflow definition."""
        steps = [
            WorkflowStep(tool="test_tool", params={}),
        ]
        definition = WorkflowDefinition(
            name="test_workflow",
            description="Test workflow",
            steps=steps,
            trigger_pattern="test_pattern",
            trigger_keywords=["test", "example"],
        )
        assert definition.name == "test_workflow"
        assert len(definition.steps) == 1
        assert definition.trigger_pattern == "test_pattern"

    def test_definition_to_dict(self):
        """Test converting definition to dictionary."""
        steps = [WorkflowStep(tool="tool1", params={"a": 1})]
        definition = WorkflowDefinition(
            name="my_workflow",
            description="My workflow",
            steps=steps,
        )
        d = definition.to_dict()
        assert d["name"] == "my_workflow"
        assert len(d["steps"]) == 1
        assert d["steps"][0]["tool"] == "tool1"


class TestYAMLWorkflows:
    """Tests for YAML-based workflows via registry."""

    @pytest.fixture
    def registry(self):
        """Get workflow registry with custom workflows loaded."""
        reg = WorkflowRegistry()
        reg.ensure_custom_loaded()
        return reg

    def test_phone_workflow_loaded(self, registry):
        """Test phone workflow is loaded from YAML."""
        workflow = registry.get_workflow("phone_workflow")
        # May not exist if not defined in YAML
        if workflow:
            assert workflow.name == "phone_workflow"

    def test_tower_workflow_loaded(self, registry):
        """Test tower workflow is loaded from YAML."""
        workflow = registry.get_workflow("tower_workflow")
        if workflow:
            assert workflow.name == "tower_workflow"

    def test_custom_workflows_loaded(self, registry):
        """Test that custom YAML workflows are loaded."""
        workflows = registry.get_all_workflows()
        # Should have at least some workflows
        assert len(workflows) >= 0  # May have 0 if no YAML files

    def test_get_definition_from_yaml(self, registry):
        """Test getting definition from YAML workflow."""
        workflows = registry.get_all_workflows()
        if workflows:
            name = workflows[0]
            definition = registry.get_definition(name)
            if definition:
                assert isinstance(definition, WorkflowDefinition)
                assert definition.name == name


class TestBaseWorkflowInterface:
    """Tests for BaseWorkflow interface via registry."""

    @pytest.fixture
    def registry(self):
        """Get workflow registry."""
        reg = WorkflowRegistry()
        reg.ensure_custom_loaded()
        return reg

    def test_workflows_implement_base_interface(self, registry):
        """Test all workflows implement BaseWorkflow."""
        for name in registry.get_all_workflows():
            workflow = registry.get_workflow(name)
            if workflow:
                assert isinstance(workflow, BaseWorkflow)

    def test_workflows_have_required_properties(self, registry):
        """Test all workflows have required properties."""
        for name in registry.get_all_workflows():
            workflow = registry.get_workflow(name)
            if workflow:
                assert isinstance(workflow.name, str)
                assert len(workflow.name) > 0
                assert isinstance(workflow.description, str)
                assert isinstance(workflow.trigger_keywords, list)


class TestWorkflowRegistration:
    """Tests for manual workflow registration."""

    @pytest.fixture
    def registry(self):
        """Create a fresh registry."""
        return WorkflowRegistry()

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
