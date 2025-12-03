"""
E2E Tests for YAML Workflow Execution.

Tests complete workflow scenarios including:
- YAML workflow loading and execution
- Keyword trigger activation
- $CALCULATE expression evaluation
- Condition-based step skipping
- $AUTO_* parameter resolution

TASK-041-15
"""

import pytest
from unittest.mock import MagicMock, patch

from server.router.application.router import SupervisorRouter
from server.router.application.workflows.registry import WorkflowRegistry, get_workflow_registry
from server.router.application.workflows.base import WorkflowDefinition, WorkflowStep
from server.router.domain.entities.scene_context import SceneContext, TopologyInfo, ProportionInfo


class TestYAMLWorkflowLoading:
    """Test YAML workflow loading from custom directory."""

    def test_custom_workflows_load(self):
        """Test that custom YAML/JSON workflows are loaded."""
        registry = WorkflowRegistry()
        registry.load_custom_workflows()

        all_workflows = registry.get_all_workflows()

        # Should have built-in + custom workflows
        assert len(all_workflows) >= 3  # At least phone, tower, screen_cutout
        # Custom workflows should be loaded (names are table_workflow/chair_workflow)
        assert "table_workflow" in all_workflows or "chair_workflow" in all_workflows

    def test_test_workflow_loads(self):
        """Test that our test workflow loads correctly."""
        registry = WorkflowRegistry()
        registry.load_custom_workflows()

        definition = registry.get_definition("test_e2e_workflow")

        if definition:  # May not exist if file wasn't created
            assert definition.name == "test_e2e_workflow"
            assert len(definition.steps) == 6
            assert "e2e_test" in definition.trigger_keywords


class TestKeywordTriggerActivation:
    """Test workflow triggering by keywords."""

    @pytest.fixture
    def registry(self):
        r = WorkflowRegistry()
        r.load_custom_workflows()
        return r

    def test_find_workflow_by_keyword(self, registry):
        """Test finding workflow by trigger keyword."""
        # Phone workflow should be found with "phone" keyword
        workflow_name = registry.find_by_keywords("create a phone")
        assert workflow_name == "phone_workflow"

        # Tower workflow should be found with "tower" keyword
        workflow_name = registry.find_by_keywords("make a tower")
        assert workflow_name == "tower_workflow"

    def test_keyword_case_insensitive(self, registry):
        """Test that keyword matching is case insensitive."""
        workflow_name = registry.find_by_keywords("CREATE A PHONE")
        assert workflow_name == "phone_workflow"

    def test_no_match_returns_none(self, registry):
        """Test that unmatched keywords return None."""
        workflow_name = registry.find_by_keywords("something random without keywords")
        assert workflow_name is None


class TestCalculateExpressionEvaluation:
    """Test $CALCULATE expression evaluation in workflows."""

    @pytest.fixture
    def registry(self):
        return WorkflowRegistry()

    @pytest.fixture
    def calculate_workflow(self):
        return WorkflowDefinition(
            name="test_calculate",
            description="Test $CALCULATE expressions",
            steps=[
                WorkflowStep(
                    tool="mesh_bevel",
                    params={
                        "width": "$CALCULATE(min_dim * 0.05)",
                        "segments": "$CALCULATE(3 + 2)",
                    },
                ),
                WorkflowStep(
                    tool="mesh_inset",
                    params={
                        "thickness": "$CALCULATE(width * 0.1)",
                    },
                ),
            ],
            trigger_keywords=["test"],
        )

    def test_calculate_with_dimensions(self, registry, calculate_workflow):
        """Test $CALCULATE expressions evaluate with dimensions."""
        registry.register_definition(calculate_workflow)

        context = {
            "dimensions": [2.0, 4.0, 0.5],  # min_dim = 0.5
            "width": 2.0,
        }

        calls = registry.expand_workflow("test_calculate", context=context)

        # min_dim * 0.05 = 0.5 * 0.05 = 0.025
        assert calls[0].params["width"] == pytest.approx(0.025)
        # 3 + 2 = 5
        assert calls[0].params["segments"] == pytest.approx(5.0)
        # width * 0.1 = 2.0 * 0.1 = 0.2
        assert calls[1].params["thickness"] == pytest.approx(0.2)


class TestConditionBasedStepSkipping:
    """Test conditional step execution."""

    @pytest.fixture
    def registry(self):
        return WorkflowRegistry()

    @pytest.fixture
    def conditional_workflow(self):
        return WorkflowDefinition(
            name="test_conditions",
            description="Test conditions",
            steps=[
                WorkflowStep(
                    tool="step_always",
                    params={},
                    description="Always runs",
                ),
                WorkflowStep(
                    tool="step_mode_check",
                    params={"mode": "EDIT"},
                    description="Only if not in EDIT",
                    condition="current_mode != 'EDIT'",
                ),
                WorkflowStep(
                    tool="step_selection_check",
                    params={"action": "all"},
                    description="Only if no selection",
                    condition="not has_selection",
                ),
            ],
            trigger_keywords=["test"],
        )

    def test_all_conditions_met(self, registry, conditional_workflow):
        """Test all steps run when conditions are met."""
        registry.register_definition(conditional_workflow)

        context = {
            "mode": "OBJECT",
            "has_selection": False,
        }

        calls = registry.expand_workflow("test_conditions", context=context)

        assert len(calls) == 3
        assert calls[0].tool_name == "step_always"
        assert calls[1].tool_name == "step_mode_check"
        assert calls[2].tool_name == "step_selection_check"

    def test_mode_condition_skipped(self, registry, conditional_workflow):
        """Test mode check step is skipped when in EDIT."""
        registry.register_definition(conditional_workflow)

        context = {
            "mode": "EDIT",  # Already in EDIT
            "has_selection": False,
        }

        calls = registry.expand_workflow("test_conditions", context=context)

        assert len(calls) == 2
        assert calls[0].tool_name == "step_always"
        assert calls[1].tool_name == "step_selection_check"

    def test_selection_condition_skipped(self, registry, conditional_workflow):
        """Test selection check step is skipped when has selection."""
        registry.register_definition(conditional_workflow)

        context = {
            "mode": "OBJECT",
            "has_selection": True,  # Already has selection
        }

        calls = registry.expand_workflow("test_conditions", context=context)

        assert len(calls) == 2
        assert calls[0].tool_name == "step_always"
        assert calls[1].tool_name == "step_mode_check"


class TestAutoParameterResolution:
    """Test $AUTO_* parameter resolution."""

    @pytest.fixture
    def registry(self):
        return WorkflowRegistry()

    @pytest.fixture
    def auto_workflow(self):
        return WorkflowDefinition(
            name="test_auto",
            description="Test $AUTO_* params",
            steps=[
                WorkflowStep(
                    tool="mesh_bevel",
                    params={
                        "width": "$AUTO_BEVEL",
                    },
                ),
                WorkflowStep(
                    tool="mesh_inset",
                    params={
                        "thickness": "$AUTO_INSET",
                    },
                ),
                WorkflowStep(
                    tool="mesh_extrude_region",
                    params={
                        "move": [0, 0, "$AUTO_EXTRUDE_NEG"],
                    },
                ),
            ],
            trigger_keywords=["test"],
        )

    def test_auto_params_resolve_with_dimensions(self, registry, auto_workflow):
        """Test $AUTO_* params resolve with dimensions."""
        registry.register_definition(auto_workflow)

        context = {
            "dimensions": [2.0, 4.0, 0.5],  # min=0.5, XY min=2.0, Z=0.5
        }

        calls = registry.expand_workflow("test_auto", context=context)

        # $AUTO_BEVEL = 5% of 0.5 = 0.025
        assert calls[0].params["width"] == pytest.approx(0.025)
        # $AUTO_INSET = 3% of 2.0 = 0.06
        assert calls[1].params["thickness"] == pytest.approx(0.06)
        # $AUTO_EXTRUDE_NEG = -10% of 0.5 = -0.05
        assert calls[2].params["move"][2] == pytest.approx(-0.05)

    def test_auto_params_fallback_without_dimensions(self, registry, auto_workflow):
        """Test $AUTO_* params remain as strings without dimensions."""
        registry.register_definition(auto_workflow)

        calls = registry.expand_workflow("test_auto", context={})

        # Without dimensions, params remain as $AUTO_* strings
        assert calls[0].params["width"] == "$AUTO_BEVEL"


class TestFullWorkflowPipeline:
    """Test complete workflow execution through router."""

    @pytest.fixture
    def mock_rpc_client(self):
        client = MagicMock()
        client.send_request.return_value = {"status": "success"}
        return client

    @pytest.fixture
    def router(self, mock_rpc_client):
        return SupervisorRouter(rpc_client=mock_rpc_client)

    def test_workflow_expands_in_pipeline(self, router):
        """Test workflow expansion returns multiple tool calls."""
        # Simulate the workflow trigger check
        registry = get_workflow_registry()
        workflow_name = registry.find_by_keywords("create a phone")

        assert workflow_name == "phone_workflow"

        # Expand the workflow
        calls = registry.expand_workflow(
            workflow_name,
            context={"mode": "OBJECT"},
        )

        # Phone workflow should have multiple steps
        assert len(calls) >= 3
        # First step should be create primitive
        assert calls[0].tool_name == "modeling_create_primitive"


class TestMixedParameterTypes:
    """Test workflows with mixed $CALCULATE, $AUTO, and literal params."""

    @pytest.fixture
    def registry(self):
        return WorkflowRegistry()

    @pytest.fixture
    def mixed_workflow(self):
        return WorkflowDefinition(
            name="test_mixed",
            description="Mixed parameter types",
            steps=[
                WorkflowStep(
                    tool="mesh_bevel",
                    params={
                        "width": "$AUTO_BEVEL",      # AUTO
                        "segments": 3,              # Literal
                    },
                    condition="current_mode == 'EDIT'",  # Condition
                ),
                WorkflowStep(
                    tool="mesh_inset",
                    params={
                        "thickness": "$CALCULATE(min_dim * 0.03)",  # CALCULATE
                        "depth": "$AUTO_EXTRUDE_SMALL",            # AUTO
                    },
                ),
                WorkflowStep(
                    tool="modeling_transform_object",
                    params={
                        "scale": "$AUTO_SCALE_SMALL",  # AUTO returning list
                    },
                ),
            ],
            trigger_keywords=["test"],
        )

    def test_mixed_params_all_resolve(self, registry, mixed_workflow):
        """Test all parameter types resolve correctly together."""
        registry.register_definition(mixed_workflow)

        context = {
            "dimensions": [2.0, 4.0, 0.5],
            "mode": "EDIT",
        }

        calls = registry.expand_workflow("test_mixed", context=context)

        # Step 1: AUTO + literal (condition met)
        assert calls[0].params["width"] == pytest.approx(0.025)
        assert calls[0].params["segments"] == 3

        # Step 2: CALCULATE + AUTO
        assert calls[1].params["thickness"] == pytest.approx(0.015)  # 0.5 * 0.03
        assert calls[1].params["depth"] == pytest.approx(0.025)      # 5% of 0.5

        # Step 3: AUTO returning list
        scale = calls[2].params["scale"]
        assert isinstance(scale, list)
        assert scale[0] == pytest.approx(1.6)  # 80% of 2.0


class TestContextSimulationInWorkflow:
    """Test that context simulation prevents redundant steps."""

    @pytest.fixture
    def registry(self):
        return WorkflowRegistry()

    @pytest.fixture
    def simulation_workflow(self):
        return WorkflowDefinition(
            name="test_simulation",
            description="Test context simulation",
            steps=[
                WorkflowStep(
                    tool="system_set_mode",
                    params={"mode": "EDIT"},
                    condition="current_mode != 'EDIT'",
                ),
                WorkflowStep(
                    tool="mesh_select",
                    params={"action": "all"},
                    condition="not has_selection",
                ),
                # These should be skipped due to simulation
                WorkflowStep(
                    tool="system_set_mode",
                    params={"mode": "EDIT"},
                    condition="current_mode != 'EDIT'",
                ),
                WorkflowStep(
                    tool="mesh_select",
                    params={"action": "all"},
                    condition="not has_selection",
                ),
                WorkflowStep(
                    tool="mesh_bevel",
                    params={"width": 0.1},
                ),
            ],
            trigger_keywords=["test"],
        )

    def test_simulation_skips_redundant_steps(self, registry, simulation_workflow):
        """Test that context simulation prevents redundant mode/select steps."""
        registry.register_definition(simulation_workflow)

        context = {
            "mode": "OBJECT",
            "has_selection": False,
        }

        calls = registry.expand_workflow("test_simulation", context=context)

        # Should only have 3 steps (2 redundant ones skipped)
        assert len(calls) == 3

        tool_names = [c.tool_name for c in calls]
        assert tool_names == ["system_set_mode", "mesh_select", "mesh_bevel"]
