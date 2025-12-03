"""
Tests for WorkflowRegistry conditional step execution.

TASK-041-11, TASK-041-12
"""

import pytest
from server.router.application.workflows.registry import WorkflowRegistry
from server.router.application.workflows.base import WorkflowDefinition, WorkflowStep


class TestRegistryConditionEvaluation:
    """Test condition evaluation in workflow expansion."""

    @pytest.fixture
    def registry(self):
        return WorkflowRegistry()

    @pytest.fixture
    def conditional_workflow(self):
        """Create a workflow with conditional steps."""
        return WorkflowDefinition(
            name="test_conditional",
            description="Test workflow with conditions",
            steps=[
                WorkflowStep(
                    tool="system_set_mode",
                    params={"mode": "EDIT"},
                    description="Switch to EDIT mode",
                    condition="current_mode != 'EDIT'",
                ),
                WorkflowStep(
                    tool="mesh_select",
                    params={"action": "all"},
                    description="Select all",
                    condition="not has_selection",
                ),
                WorkflowStep(
                    tool="mesh_bevel",
                    params={"width": 0.1, "segments": 3},
                    description="Bevel edges",
                ),
            ],
            trigger_keywords=["test"],
        )

    def test_all_conditions_met(self, registry, conditional_workflow):
        """Test when all conditions are met - all steps execute."""
        registry.register_definition(conditional_workflow)

        # Context: OBJECT mode, no selection
        context = {
            "mode": "OBJECT",
            "has_selection": False,
        }

        calls = registry.expand_workflow("test_conditional", context=context)

        # All 3 steps should execute
        assert len(calls) == 3
        assert calls[0].tool_name == "system_set_mode"
        assert calls[1].tool_name == "mesh_select"
        assert calls[2].tool_name == "mesh_bevel"

    def test_mode_condition_not_met(self, registry, conditional_workflow):
        """Test when already in EDIT mode - mode switch is skipped."""
        registry.register_definition(conditional_workflow)

        # Context: Already in EDIT mode
        context = {
            "mode": "EDIT",
            "has_selection": False,
        }

        calls = registry.expand_workflow("test_conditional", context=context)

        # Mode switch should be skipped, 2 steps execute
        assert len(calls) == 2
        assert calls[0].tool_name == "mesh_select"
        assert calls[1].tool_name == "mesh_bevel"

    def test_selection_condition_not_met(self, registry, conditional_workflow):
        """Test when already has selection - select all is skipped."""
        registry.register_definition(conditional_workflow)

        # Context: OBJECT mode, has selection
        context = {
            "mode": "OBJECT",
            "has_selection": True,
        }

        calls = registry.expand_workflow("test_conditional", context=context)

        # Select all should be skipped, 2 steps execute
        assert len(calls) == 2
        assert calls[0].tool_name == "system_set_mode"
        assert calls[1].tool_name == "mesh_bevel"

    def test_both_conditions_not_met(self, registry, conditional_workflow):
        """Test when both conditions are not met - only unconditional step executes."""
        registry.register_definition(conditional_workflow)

        # Context: Already in EDIT mode AND has selection
        context = {
            "mode": "EDIT",
            "has_selection": True,
        }

        calls = registry.expand_workflow("test_conditional", context=context)

        # Only bevel (no condition) should execute
        assert len(calls) == 1
        assert calls[0].tool_name == "mesh_bevel"

    def test_no_context_partial_execution(self, registry, conditional_workflow):
        """Test when no context provided.

        Behavior:
        - "current_mode != 'EDIT'" - current_mode unknown, fails-open → True → executes
        - "not has_selection" - has_selection unknown → inner fails-open → True → not True → False → skipped
        - no condition → executes
        """
        registry.register_definition(conditional_workflow)

        calls = registry.expand_workflow("test_conditional", context=None)

        # 2 steps execute (mode switch and bevel), select is skipped
        assert len(calls) == 2
        assert calls[0].tool_name == "system_set_mode"
        assert calls[1].tool_name == "mesh_bevel"


class TestContextSimulation:
    """Test context simulation during workflow expansion (TASK-041-12)."""

    @pytest.fixture
    def registry(self):
        return WorkflowRegistry()

    @pytest.fixture
    def simulation_workflow(self):
        """Create a workflow that tests context simulation."""
        return WorkflowDefinition(
            name="test_simulation",
            description="Test context simulation",
            steps=[
                # Step 1: Switch to EDIT mode (always runs first time)
                WorkflowStep(
                    tool="system_set_mode",
                    params={"mode": "EDIT"},
                    description="Switch to EDIT mode",
                    condition="current_mode != 'EDIT'",
                ),
                # Step 2: Select all (should run - simulation shows no selection yet)
                WorkflowStep(
                    tool="mesh_select",
                    params={"action": "all"},
                    description="Select all",
                    condition="not has_selection",
                ),
                # Step 3: Another mode check - should NOT run (simulation shows EDIT)
                WorkflowStep(
                    tool="system_set_mode",
                    params={"mode": "EDIT"},
                    description="Redundant mode switch",
                    condition="current_mode != 'EDIT'",
                ),
                # Step 4: Another select all - should NOT run (simulation shows selected)
                WorkflowStep(
                    tool="mesh_select",
                    params={"action": "all"},
                    description="Redundant select all",
                    condition="not has_selection",
                ),
                # Step 5: Unconditional step
                WorkflowStep(
                    tool="mesh_bevel",
                    params={"width": 0.1},
                    description="Bevel",
                ),
            ],
            trigger_keywords=["test"],
        )

    def test_context_simulation_prevents_redundant_steps(
        self, registry, simulation_workflow
    ):
        """Test that context simulation prevents redundant conditional steps."""
        registry.register_definition(simulation_workflow)

        # Start in OBJECT mode, no selection
        context = {
            "mode": "OBJECT",
            "has_selection": False,
        }

        calls = registry.expand_workflow("test_simulation", context=context)

        # Expected:
        # 1. system_set_mode - runs (OBJECT != EDIT)
        # 2. mesh_select all - runs (no selection)
        # 3. system_set_mode - SKIPPED (simulation says now in EDIT)
        # 4. mesh_select all - SKIPPED (simulation says has selection)
        # 5. mesh_bevel - runs (no condition)
        assert len(calls) == 3

        assert calls[0].tool_name == "system_set_mode"
        assert calls[1].tool_name == "mesh_select"
        assert calls[2].tool_name == "mesh_bevel"


class TestNumericConditions:
    """Test numeric comparisons in conditions."""

    @pytest.fixture
    def registry(self):
        return WorkflowRegistry()

    @pytest.fixture
    def numeric_workflow(self):
        """Create a workflow with numeric conditions."""
        return WorkflowDefinition(
            name="test_numeric",
            description="Test numeric conditions",
            steps=[
                WorkflowStep(
                    tool="mesh_subdivide",
                    params={"number_cuts": 2},
                    description="Subdivide if enough vertices",
                    condition="selected_verts >= 4",
                ),
                WorkflowStep(
                    tool="mesh_delete_selected",
                    params={},
                    description="Delete if any selection",
                    condition="selected_faces > 0",
                ),
            ],
            trigger_keywords=["test"],
        )

    def test_numeric_condition_met(self, registry, numeric_workflow):
        """Test when numeric conditions are met."""
        registry.register_definition(numeric_workflow)

        context = {
            "selected_verts": 8,
            "selected_faces": 2,
        }

        calls = registry.expand_workflow("test_numeric", context=context)

        assert len(calls) == 2

    def test_numeric_condition_not_met(self, registry, numeric_workflow):
        """Test when numeric conditions are not met."""
        registry.register_definition(numeric_workflow)

        context = {
            "selected_verts": 2,  # < 4
            "selected_faces": 0,  # not > 0
        }

        calls = registry.expand_workflow("test_numeric", context=context)

        assert len(calls) == 0


class TestLogicalConditions:
    """Test logical operators in conditions."""

    @pytest.fixture
    def registry(self):
        return WorkflowRegistry()

    @pytest.fixture
    def logical_workflow(self):
        """Create a workflow with logical conditions."""
        return WorkflowDefinition(
            name="test_logical",
            description="Test logical conditions",
            steps=[
                WorkflowStep(
                    tool="mesh_extrude_region",
                    params={"move": [0, 0, 1]},
                    description="Extrude if EDIT mode AND has selection",
                    condition="current_mode == 'EDIT' and has_selection",
                ),
                WorkflowStep(
                    tool="mesh_select",
                    params={"action": "all"},
                    description="Select if OBJECT mode OR no selection",
                    condition="current_mode == 'OBJECT' or not has_selection",
                ),
            ],
            trigger_keywords=["test"],
        )

    def test_and_condition(self, registry, logical_workflow):
        """Test AND condition."""
        registry.register_definition(logical_workflow)

        # Both conditions true
        context = {
            "mode": "EDIT",
            "has_selection": True,
        }

        calls = registry.expand_workflow("test_logical", context=context)

        # Extrude runs (EDIT and selection), select skipped (not OBJECT and has selection)
        assert len(calls) == 1
        assert calls[0].tool_name == "mesh_extrude_region"

    def test_or_condition(self, registry, logical_workflow):
        """Test OR condition."""
        registry.register_definition(logical_workflow)

        # OBJECT mode but has selection
        context = {
            "mode": "OBJECT",
            "has_selection": True,
        }

        calls = registry.expand_workflow("test_logical", context=context)

        # Extrude skipped (not EDIT), select runs (OBJECT mode)
        assert len(calls) == 1
        assert calls[0].tool_name == "mesh_select"
