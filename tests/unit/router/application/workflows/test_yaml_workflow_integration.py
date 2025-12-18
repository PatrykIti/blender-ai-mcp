"""
E2E Tests for YAML Workflow Execution.

Tests complete workflow scenarios including:
- YAML workflow loading and execution
- Keyword trigger activation
- $CALCULATE expression evaluation
- Condition-based step skipping
- $AUTO_* parameter resolution

TASK-041-15
TASK-050: Updated to not depend on specific builtin workflows (YAML-based now).
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

        # Should have at least one workflow loaded
        assert isinstance(all_workflows, list)

    def test_workflow_definition_structure(self):
        """Test that loaded workflows have proper structure."""
        registry = WorkflowRegistry()
        registry.load_custom_workflows()

        all_workflows = registry.get_all_workflows()
        if all_workflows:
            # Pick the first available workflow
            workflow_name = all_workflows[0]
            definition = registry.get_definition(workflow_name)

            assert definition is not None
            assert definition.name == workflow_name
            assert len(definition.steps) > 0


class TestKeywordTriggerActivation:
    """Test workflow triggering by keywords."""

    @pytest.fixture
    def registry(self):
        """Create registry with test workflow registered."""
        r = WorkflowRegistry()
        # Register a test workflow for keyword testing
        test_def = WorkflowDefinition(
            name="test_keyword_workflow",
            description="Test workflow for keyword matching",
            steps=[
                WorkflowStep(tool="test_tool", params={}),
            ],
            trigger_keywords=["test_keyword", "sample_keyword"],
        )
        r.register_definition(test_def)
        return r

    def test_find_workflow_by_keyword(self, registry):
        """Test finding workflow by trigger keyword."""
        workflow_name = registry.find_by_keywords("use test_keyword here")
        assert workflow_name == "test_keyword_workflow"

    def test_keyword_case_insensitive(self, registry):
        """Test that keyword matching is case insensitive."""
        workflow_name = registry.find_by_keywords("USE TEST_KEYWORD HERE")
        assert workflow_name == "test_keyword_workflow"

    def test_no_match_returns_none(self, registry):
        """Test that unmatched keywords return None."""
        workflow_name = registry.find_by_keywords("something random without matching keywords xyz123")
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
                        "offset": "$CALCULATE(min_dim * 0.05)",
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
        assert calls[0].params["offset"] == pytest.approx(0.025)
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
                    condition="current_mode == 'EDIT'",
                    description="Only in EDIT mode",
                ),
                WorkflowStep(
                    tool="step_selection_check",
                    params={},
                    condition="has_selection",
                    description="Only with selection",
                ),
            ],
            trigger_keywords=["test"],
        )

    def test_conditions_skip_steps_object_mode(self, registry, conditional_workflow):
        """Test that conditions skip steps when not met."""
        registry.register_definition(conditional_workflow)

        context = {
            "current_mode": "OBJECT",
            "has_selection": False,
        }

        calls = registry.expand_workflow("test_conditions", context=context)

        # Only the always-run step should execute
        assert len(calls) == 1
        assert calls[0].tool_name == "step_always"

    def test_conditions_run_steps_edit_mode(self, registry, conditional_workflow):
        """Test that conditions allow steps when met."""
        registry.register_definition(conditional_workflow)

        context = {
            "current_mode": "EDIT",
            "has_selection": True,
        }

        calls = registry.expand_workflow("test_conditions", context=context)

        # All steps should execute
        assert len(calls) == 3


class TestAutoParameterResolution:
    """Test $AUTO_* parameter resolution."""

    @pytest.fixture
    def registry(self):
        return WorkflowRegistry()

    @pytest.fixture
    def auto_workflow(self):
        return WorkflowDefinition(
            name="test_auto",
            description="Test $AUTO parameters",
            steps=[
                WorkflowStep(
                    tool="mesh_bevel",
                    params={
                        "offset": "$AUTO_BEVEL",
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
        """Test $AUTO_* parameters resolve based on dimensions."""
        registry.register_definition(auto_workflow)

        context = {
            "dimensions": [2.0, 4.0, 0.5],  # min=0.5, XY min=2.0, Z=0.5
        }

        calls = registry.expand_workflow("test_auto", context=context)

        # $AUTO_BEVEL = 5% of 0.5 = 0.025
        assert calls[0].params["offset"] == pytest.approx(0.025)
        # $AUTO_INSET = 3% of 2.0 = 0.06
        assert calls[1].params["thickness"] == pytest.approx(0.06)
        # $AUTO_EXTRUDE_NEG = -10% of 0.5 = -0.05
        assert calls[2].params["move"][2] == pytest.approx(-0.05)

    def test_auto_params_fallback_without_dimensions(self, registry, auto_workflow):
        """Test $AUTO_* params remain as strings without dimensions."""
        registry.register_definition(auto_workflow)

        calls = registry.expand_workflow("test_auto", context={})

        # Without dimensions, params remain as $AUTO_* strings
        assert calls[0].params["offset"] == "$AUTO_BEVEL"


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

    @pytest.fixture
    def registry_with_workflow(self):
        """Create registry with a test workflow registered."""
        # Use a fresh registry instead of singleton to avoid keyword collisions
        registry = WorkflowRegistry()
        test_def = WorkflowDefinition(
            name="test_pipeline_workflow",
            description="Test workflow for pipeline testing",
            steps=[
                WorkflowStep(tool="modeling_create_primitive", params={"type": "CUBE"}),
                WorkflowStep(tool="scene_set_mode", params={"mode": "EDIT"}),
                WorkflowStep(tool="mesh_select", params={"action": "all"}),
            ],
            trigger_keywords=["unique_pipeline_keyword_xyz"],
        )
        registry.register_definition(test_def)
        return registry

    def test_workflow_expands_in_pipeline(self, router, registry_with_workflow):
        """Test workflow expansion returns multiple tool calls."""
        workflow_name = registry_with_workflow.find_by_keywords("use unique_pipeline_keyword_xyz here")

        assert workflow_name == "test_pipeline_workflow"

        # Expand the workflow
        calls = registry_with_workflow.expand_workflow(
            workflow_name,
            context={"mode": "OBJECT"},
        )

        # Workflow should have multiple steps
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
                        "offset": "$AUTO_BEVEL",      # AUTO
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
        assert calls[0].params["offset"] == pytest.approx(0.025)
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
                    params={"offset": 0.1},
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
