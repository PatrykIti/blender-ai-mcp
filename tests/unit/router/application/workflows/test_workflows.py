"""
Unit tests for workflow definitions.

Tests for PhoneWorkflow, TowerWorkflow, ScreenCutoutWorkflow.
TASK-039-19, TASK-039-20, TASK-039-21
"""

import pytest

from server.router.application.workflows.base import (
    BaseWorkflow,
    WorkflowDefinition,
    WorkflowStep,
)
from server.router.application.workflows.phone_workflow import (
    PhoneWorkflow,
    phone_workflow,
)
from server.router.application.workflows.tower_workflow import (
    TowerWorkflow,
    tower_workflow,
)
from server.router.application.workflows.screen_cutout_workflow import (
    ScreenCutoutWorkflow,
    screen_cutout_workflow,
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


class TestPhoneWorkflow:
    """Tests for PhoneWorkflow."""

    def test_workflow_properties(self):
        """Test workflow basic properties."""
        assert phone_workflow.name == "phone_workflow"
        assert "phone" in phone_workflow.description.lower()
        assert phone_workflow.trigger_pattern == "phone_like"

    def test_trigger_keywords(self):
        """Test workflow trigger keywords."""
        keywords = phone_workflow.trigger_keywords
        assert "phone" in keywords
        assert "smartphone" in keywords
        assert "tablet" in keywords

    def test_default_steps(self):
        """Test getting default workflow steps."""
        steps = phone_workflow.get_steps()
        assert len(steps) == 10  # 10 steps in phone workflow

        # Verify step tools
        tool_names = [s.tool for s in steps]
        assert "modeling_create_primitive" in tool_names
        assert "mesh_bevel" in tool_names
        assert "mesh_inset" in tool_names
        assert "mesh_extrude_region" in tool_names

    def test_custom_parameters(self):
        """Test workflow with custom parameters."""
        steps = phone_workflow.get_steps({
            "width": 0.5,
            "height": 1.0,
            "bevel_width": 0.05,
        })

        # Find scale step
        scale_step = next(s for s in steps if s.tool == "modeling_transform_object")
        assert scale_step.params["scale"][0] == 0.5
        assert scale_step.params["scale"][1] == 1.0

    def test_get_definition(self):
        """Test getting complete workflow definition."""
        definition = phone_workflow.get_definition()
        assert isinstance(definition, WorkflowDefinition)
        assert definition.name == "phone_workflow"
        assert len(definition.steps) == 10

    def test_matches_pattern(self):
        """Test pattern matching."""
        assert phone_workflow.matches_pattern("phone_like")
        assert not phone_workflow.matches_pattern("tower_like")

    def test_matches_keywords(self):
        """Test keyword matching."""
        assert phone_workflow.matches_keywords("create a smartphone")
        assert phone_workflow.matches_keywords("make tablet")
        assert not phone_workflow.matches_keywords("create tower")

    def test_get_variant_smartphone(self):
        """Test smartphone variant parameters."""
        variant = phone_workflow.get_variant("smartphone")
        assert variant is not None
        assert variant["width"] == 0.07
        assert variant["height"] == 0.15

    def test_get_variant_tablet(self):
        """Test tablet variant parameters."""
        variant = phone_workflow.get_variant("tablet")
        assert variant is not None
        assert variant["width"] == 0.18

    def test_get_variant_unknown(self):
        """Test unknown variant returns None."""
        assert phone_workflow.get_variant("unknown") is None


class TestTowerWorkflow:
    """Tests for TowerWorkflow."""

    def test_workflow_properties(self):
        """Test workflow basic properties."""
        assert tower_workflow.name == "tower_workflow"
        assert "tower" in tower_workflow.description.lower()
        assert tower_workflow.trigger_pattern == "tower_like"

    def test_trigger_keywords(self):
        """Test workflow trigger keywords."""
        keywords = tower_workflow.trigger_keywords
        assert "tower" in keywords
        assert "pillar" in keywords
        assert "column" in keywords

    def test_default_steps_with_taper(self):
        """Test getting default workflow steps with taper."""
        steps = tower_workflow.get_steps()
        # Should have taper steps by default
        assert len(steps) >= 7

        tool_names = [s.tool for s in steps]
        assert "modeling_create_primitive" in tool_names
        assert "mesh_subdivide" in tool_names
        assert "mesh_transform_selected" in tool_names

    def test_steps_without_taper(self):
        """Test workflow without taper effect."""
        steps = tower_workflow.get_steps({"add_taper": False})
        # Fewer steps without taper
        tool_names = [s.tool for s in steps]
        assert "mesh_transform_selected" not in tool_names

    def test_custom_height(self):
        """Test workflow with custom height."""
        steps = tower_workflow.get_steps({"height": 5.0})
        scale_step = next(s for s in steps if s.tool == "modeling_transform_object")
        assert scale_step.params["scale"][2] == 5.0

    def test_matches_pattern(self):
        """Test pattern matching."""
        assert tower_workflow.matches_pattern("tower_like")
        assert not tower_workflow.matches_pattern("phone_like")

    def test_get_variant_obelisk(self):
        """Test obelisk variant."""
        variant = tower_workflow.get_variant("obelisk")
        assert variant is not None
        assert variant["taper_factor"] == 0.4

    def test_get_variant_spire(self):
        """Test spire variant."""
        variant = tower_workflow.get_variant("spire")
        assert variant is not None
        assert variant["taper_factor"] == 0.1  # Sharp point


class TestScreenCutoutWorkflow:
    """Tests for ScreenCutoutWorkflow."""

    def test_workflow_properties(self):
        """Test workflow basic properties."""
        assert screen_cutout_workflow.name == "screen_cutout_workflow"
        assert "screen" in screen_cutout_workflow.description.lower()

    def test_trigger_keywords(self):
        """Test workflow trigger keywords."""
        keywords = screen_cutout_workflow.trigger_keywords
        assert "screen" in keywords
        assert "display" in keywords
        assert "button" in keywords

    def test_default_steps_with_bevel(self):
        """Test getting default workflow steps with bevel."""
        steps = screen_cutout_workflow.get_steps()
        assert len(steps) == 4  # With bevel by default

        tool_names = [s.tool for s in steps]
        assert "mesh_select_targeted" in tool_names
        assert "mesh_inset" in tool_names
        assert "mesh_extrude_region" in tool_names
        assert "mesh_bevel" in tool_names

    def test_steps_without_bevel(self):
        """Test workflow without bevel."""
        steps = screen_cutout_workflow.get_steps({"add_bevel": False})
        assert len(steps) == 3
        tool_names = [s.tool for s in steps]
        assert "mesh_bevel" not in tool_names

    def test_custom_inset_thickness(self):
        """Test workflow with custom inset thickness."""
        steps = screen_cutout_workflow.get_steps({"inset_thickness": 0.1})
        inset_step = next(s for s in steps if s.tool == "mesh_inset")
        assert inset_step.params["thickness"] == 0.1

    def test_get_variant_button(self):
        """Test button variant."""
        variant = screen_cutout_workflow.get_variant("button")
        assert variant is not None
        assert variant["inset_thickness"] == 0.01

    def test_get_variant_deep_recess(self):
        """Test deep recess variant."""
        variant = screen_cutout_workflow.get_variant("deep_recess")
        assert variant is not None
        assert variant["extrude_depth"] == 0.1
        assert variant["add_bevel"] is False


class TestBaseWorkflowInterface:
    """Tests for BaseWorkflow interface."""

    def test_phone_workflow_is_base_workflow(self):
        """Test PhoneWorkflow implements BaseWorkflow."""
        assert isinstance(phone_workflow, BaseWorkflow)

    def test_tower_workflow_is_base_workflow(self):
        """Test TowerWorkflow implements BaseWorkflow."""
        assert isinstance(tower_workflow, BaseWorkflow)

    def test_screen_cutout_is_base_workflow(self):
        """Test ScreenCutoutWorkflow implements BaseWorkflow."""
        assert isinstance(screen_cutout_workflow, BaseWorkflow)

    def test_all_workflows_have_required_properties(self):
        """Test all workflows have required properties."""
        workflows = [phone_workflow, tower_workflow, screen_cutout_workflow]

        for workflow in workflows:
            assert isinstance(workflow.name, str)
            assert len(workflow.name) > 0
            assert isinstance(workflow.description, str)
            assert isinstance(workflow.trigger_keywords, list)
            assert len(workflow.get_steps()) > 0
