"""
Tests for WorkflowRegistry ProportionResolver integration.

TASK-041-14
"""

import pytest
from server.router.application.workflows.registry import WorkflowRegistry
from server.router.application.workflows.base import WorkflowDefinition, WorkflowStep


class TestRegistryProportionResolver:
    """Test ProportionResolver integration in workflow expansion."""

    @pytest.fixture
    def registry(self):
        return WorkflowRegistry()

    @pytest.fixture
    def auto_param_workflow(self):
        """Create a workflow with $AUTO_* parameters."""
        return WorkflowDefinition(
            name="test_auto_params",
            description="Test workflow with AUTO params",
            steps=[
                WorkflowStep(
                    tool="mesh_bevel",
                    params={
                        "offset": "$AUTO_BEVEL",
                        "segments": 3,
                    },
                    description="Auto bevel",
                ),
                WorkflowStep(
                    tool="mesh_inset",
                    params={
                        "thickness": "$AUTO_INSET",
                    },
                    description="Auto inset",
                ),
                WorkflowStep(
                    tool="mesh_extrude_region",
                    params={
                        "move": [0, 0, "$AUTO_EXTRUDE_NEG"],
                    },
                    description="Auto extrude",
                ),
            ],
            trigger_keywords=["test"],
        )

    def test_auto_params_with_dimensions(self, registry, auto_param_workflow):
        """Test $AUTO_* params are resolved when dimensions provided."""
        registry.register_definition(auto_param_workflow)

        context = {
            "dimensions": [2.0, 4.0, 0.5],  # min=0.5, XY min=2.0, Z=0.5
        }

        calls = registry.expand_workflow("test_auto_params", context=context)

        assert len(calls) == 3

        # $AUTO_BEVEL = 5% of min(0.5) = 0.025
        assert calls[0].params["offset"] == pytest.approx(0.025)
        assert calls[0].params["segments"] == 3

        # $AUTO_INSET = 3% of XY min(2.0) = 0.06
        assert calls[1].params["thickness"] == pytest.approx(0.06)

        # $AUTO_EXTRUDE_NEG = -10% of Z(0.5) = -0.05
        assert calls[2].params["move"][2] == pytest.approx(-0.05)

    def test_auto_params_without_dimensions(self, registry, auto_param_workflow):
        """Test $AUTO_* params remain as-is when no dimensions."""
        registry.register_definition(auto_param_workflow)

        # No dimensions in context
        calls = registry.expand_workflow("test_auto_params", context={})

        # Params should remain as $AUTO_* strings
        assert calls[0].params["offset"] == "$AUTO_BEVEL"
        assert calls[1].params["thickness"] == "$AUTO_INSET"
        assert calls[2].params["move"][2] == "$AUTO_EXTRUDE_NEG"

    def test_auto_params_with_width_height_depth(self, registry, auto_param_workflow):
        """Test dimensions can be provided as width/height/depth."""
        registry.register_definition(auto_param_workflow)

        context = {
            "width": 2.0,
            "height": 4.0,
            "depth": 0.5,
        }

        calls = registry.expand_workflow("test_auto_params", context=context)

        # Should resolve same as dimensions array
        assert calls[0].params["offset"] == pytest.approx(0.025)


class TestMixedParameters:
    """Test workflows with mixed parameter types."""

    @pytest.fixture
    def registry(self):
        return WorkflowRegistry()

    @pytest.fixture
    def mixed_workflow(self):
        """Create a workflow with mixed $CALCULATE, $AUTO, and literal params."""
        return WorkflowDefinition(
            name="test_mixed",
            description="Test workflow with mixed params",
            steps=[
                WorkflowStep(
                    tool="mesh_bevel",
                    params={
                        "offset": "$AUTO_BEVEL",  # ProportionResolver
                        "segments": 3,  # Literal
                    },
                    description="Mixed params",
                ),
                WorkflowStep(
                    tool="mesh_inset",
                    params={
                        "thickness": "$CALCULATE(min_dim * 0.03)",  # ExpressionEvaluator
                    },
                    description="Calculate param",
                ),
            ],
            trigger_keywords=["test"],
        )

    def test_mixed_params_resolved(self, registry, mixed_workflow):
        """Test both $AUTO_* and $CALCULATE params resolve."""
        registry.register_definition(mixed_workflow)

        context = {
            "dimensions": [2.0, 4.0, 0.5],  # min_dim = 0.5
        }

        calls = registry.expand_workflow("test_mixed", context=context)

        # $AUTO_BEVEL = 5% of 0.5 = 0.025
        assert calls[0].params["offset"] == pytest.approx(0.025)
        assert calls[0].params["segments"] == 3

        # $CALCULATE(min_dim * 0.03) = 0.5 * 0.03 = 0.015
        assert calls[1].params["thickness"] == pytest.approx(0.015)


class TestAutoScaleParams:
    """Test $AUTO_SCALE_* parameters that return lists."""

    @pytest.fixture
    def registry(self):
        return WorkflowRegistry()

    @pytest.fixture
    def scale_workflow(self):
        """Create a workflow with scale parameters."""
        return WorkflowDefinition(
            name="test_scale",
            description="Test scale params",
            steps=[
                WorkflowStep(
                    tool="modeling_transform_object",
                    params={
                        "scale": "$AUTO_SCALE_SMALL",
                    },
                    description="Scale down",
                ),
            ],
            trigger_keywords=["test"],
        )

    def test_auto_scale_returns_list(self, registry, scale_workflow):
        """Test $AUTO_SCALE_* returns a list of values."""
        registry.register_definition(scale_workflow)

        context = {
            "dimensions": [2.0, 4.0, 0.5],
        }

        calls = registry.expand_workflow("test_scale", context=context)

        # $AUTO_SCALE_SMALL = 80% of each dimension
        scale = calls[0].params["scale"]
        assert isinstance(scale, list)
        assert len(scale) == 3
        assert scale[0] == pytest.approx(1.6)   # 80% of 2.0
        assert scale[1] == pytest.approx(3.2)   # 80% of 4.0
        assert scale[2] == pytest.approx(0.4)   # 80% of 0.5


class TestRealWorldWorkflows:
    """Test real-world workflow scenarios."""

    @pytest.fixture
    def registry(self):
        return WorkflowRegistry()

    @pytest.fixture
    def phone_style_workflow(self):
        """Create a phone-style workflow with AUTO params."""
        return WorkflowDefinition(
            name="phone_auto",
            description="Phone with auto params",
            steps=[
                WorkflowStep(
                    tool="modeling_create_primitive",
                    params={"type": "CUBE"},
                ),
                WorkflowStep(
                    tool="system_set_mode",
                    params={"mode": "EDIT"},
                ),
                WorkflowStep(
                    tool="mesh_select",
                    params={"action": "all"},
                ),
                WorkflowStep(
                    tool="mesh_bevel",
                    params={
                        "offset": "$AUTO_BEVEL",
                        "segments": 3,
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
                        "move": [0, 0, "$AUTO_SCREEN_DEPTH_NEG"],
                    },
                ),
            ],
            trigger_keywords=["phone"],
        )

    def test_phone_workflow_with_realistic_dims(self, registry, phone_style_workflow):
        """Test phone workflow with realistic phone dimensions."""
        registry.register_definition(phone_style_workflow)

        # Phone: 7cm x 15cm x 8mm (0.07 x 0.15 x 0.008 meters)
        context = {
            "dimensions": [0.07, 0.15, 0.008],
            "mode": "OBJECT",
        }

        calls = registry.expand_workflow("phone_auto", context=context)

        assert len(calls) == 6

        # Bevel: 5% of min(0.008) = 0.0004
        assert calls[3].params["offset"] == pytest.approx(0.0004)

        # Inset: 3% of XY min(0.07) = 0.0021
        assert calls[4].params["thickness"] == pytest.approx(0.0021)

        # Screen depth: -50% of Z(0.008) = -0.004
        assert calls[5].params["move"][2] == pytest.approx(-0.004)
