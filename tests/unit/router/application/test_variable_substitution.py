"""
Unit tests for TASK-052: Parametric Variable Substitution.

Tests the extract_modifiers() and substitute_variables() functions
for workflow parametric adaptation.
"""

import pytest

from server.router.application.engines.workflow_expansion_engine import (
    extract_modifiers,
    substitute_variables,
    _substitute_list,
)
from server.router.application.workflows.registry import get_workflow_registry
from server.router.application.workflows.base import WorkflowDefinition, WorkflowStep


class TestExtractModifiers:
    """Tests for extract_modifiers function."""

    def test_single_modifier_match(self):
        """Test matching a single modifier keyword."""
        modifiers = {
            "straight legs": {"leg_angle": 0},
            "angled legs": {"leg_angle": 0.32},
        }

        result = extract_modifiers("table with straight legs", modifiers)

        assert result == {"leg_angle": 0}

    def test_case_insensitive_match(self):
        """Test that matching is case insensitive."""
        modifiers = {
            "Straight Legs": {"leg_angle": 0},
        }

        result = extract_modifiers("TABLE WITH STRAIGHT LEGS", modifiers)

        assert result == {"leg_angle": 0}

    def test_no_match_returns_empty(self):
        """Test that no match returns empty dict."""
        modifiers = {
            "straight legs": {"leg_angle": 0},
        }

        result = extract_modifiers("table with wheels", modifiers)

        assert result == {}

    def test_multiple_modifiers_merge(self):
        """Test that multiple matching modifiers merge."""
        modifiers = {
            "straight legs": {"leg_angle": 0},
            "coffee table": {"height": 0.15},
        }

        result = extract_modifiers("straight legs coffee table", modifiers)

        assert result == {"leg_angle": 0, "height": 0.15}

    def test_later_match_overrides_earlier(self):
        """Test that later matches override earlier ones."""
        # Note: Dict order depends on Python version (3.7+ preserves insertion order)
        modifiers = {
            "small": {"size": 1},
            "large": {"size": 3},
        }

        result = extract_modifiers("small but actually large table", modifiers)

        # Both match, but 'large' was processed later so it overrides
        assert result["size"] == 3

    def test_polish_keywords(self):
        """Test Polish keyword matching."""
        modifiers = {
            "proste nogi": {"leg_angle": 0},
            "skośne nogi": {"leg_angle": 0.32},
        }

        result = extract_modifiers("stół z proste nogi", modifiers)

        assert result == {"leg_angle": 0}

    def test_partial_match(self):
        """Test that partial substring matches work."""
        modifiers = {
            "straight": {"angle": 0},
        }

        result = extract_modifiers("make it straightforward", modifiers)

        # "straight" is in "straightforward"
        assert result == {"angle": 0}

    def test_empty_modifiers(self):
        """Test with empty modifiers dict."""
        result = extract_modifiers("any prompt", {})

        assert result == {}

    def test_empty_prompt(self):
        """Test with empty prompt."""
        modifiers = {
            "straight": {"angle": 0},
        }

        result = extract_modifiers("", modifiers)

        assert result == {}


class TestSubstituteVariables:
    """Tests for substitute_variables function."""

    def test_simple_variable_substitution(self):
        """Test simple $variable substitution."""
        params = {"name": "Leg", "angle": "$leg_angle"}
        variables = {"leg_angle": 0.32}

        result = substitute_variables(params, variables)

        assert result == {"name": "Leg", "angle": 0.32}

    def test_list_variable_substitution(self):
        """Test $variable substitution in lists."""
        params = {"rotation": [0, "$angle", 0]}
        variables = {"angle": 0.5}

        result = substitute_variables(params, variables)

        assert result == {"rotation": [0, 0.5, 0]}

    def test_mixed_list_values(self):
        """Test list with mixed static and variable values."""
        params = {"scale": [1.0, "$scale_y", 2.0]}
        variables = {"scale_y": 1.5}

        result = substitute_variables(params, variables)

        assert result == {"scale": [1.0, 1.5, 2.0]}

    def test_undefined_variable_kept(self):
        """Test that undefined variables are kept as-is."""
        params = {"value": "$unknown_var"}
        variables = {}

        result = substitute_variables(params, variables)

        assert result == {"value": "$unknown_var"}

    def test_calculate_expression_kept(self):
        """Test that $CALCULATE expressions are kept for later processing."""
        params = {"width": "$CALCULATE(min_dim * 0.05)"}
        variables = {}

        result = substitute_variables(params, variables)

        # $CALCULATE should not be substituted by this function
        assert result == {"width": "$CALCULATE(min_dim * 0.05)"}

    def test_auto_expression_kept(self):
        """Test that $AUTO_* expressions are kept for later processing."""
        params = {"inset": "$AUTO_INSET"}
        variables = {}

        result = substitute_variables(params, variables)

        assert result == {"inset": "$AUTO_INSET"}

    def test_nested_dict_substitution(self):
        """Test variable substitution in nested dicts."""
        params = {
            "transform": {
                "location": [0, 0, "$height"],
                "scale": [1, 1, 1],
            }
        }
        variables = {"height": 2.5}

        result = substitute_variables(params, variables)

        assert result["transform"]["location"] == [0, 0, 2.5]

    def test_non_string_values_unchanged(self):
        """Test that non-string values are unchanged."""
        params = {"count": 5, "enabled": True, "scale": 1.5}
        variables = {}

        result = substitute_variables(params, variables)

        assert result == {"count": 5, "enabled": True, "scale": 1.5}

    def test_empty_params(self):
        """Test with empty params."""
        result = substitute_variables({}, {"var": 1})

        assert result == {}

    def test_empty_variables(self):
        """Test with empty variables."""
        params = {"name": "Test", "value": "$var"}

        result = substitute_variables(params, {})

        assert result == {"name": "Test", "value": "$var"}

    def test_multiple_variables_in_list(self):
        """Test multiple variables in same list."""
        params = {"vec": ["$x", "$y", "$z"]}
        variables = {"x": 1, "y": 2, "z": 3}

        result = substitute_variables(params, variables)

        assert result == {"vec": [1, 2, 3]}


class TestSubstituteList:
    """Tests for _substitute_list helper function."""

    def test_simple_list(self):
        """Test simple list substitution."""
        lst = [1, "$var", 3]
        variables = {"var": 2}

        result = _substitute_list(lst, variables)

        assert result == [1, 2, 3]

    def test_nested_list(self):
        """Test nested list substitution."""
        lst = [[1, "$a"], [2, "$b"]]
        variables = {"a": 10, "b": 20}

        result = _substitute_list(lst, variables)

        assert result == [[1, 10], [2, 20]]

    def test_dict_in_list(self):
        """Test dict inside list."""
        lst = [{"key": "$val"}]
        variables = {"val": 42}

        result = _substitute_list(lst, variables)

        assert result == [{"key": 42}]


class TestWorkflowDefinitionWithModifiers:
    """Tests for WorkflowDefinition with defaults and modifiers."""

    def test_definition_with_defaults(self):
        """Test creating definition with defaults."""
        definition = WorkflowDefinition(
            name="test_workflow",
            description="Test",
            steps=[],
            defaults={"angle": 0.32, "height": 1.0},
        )

        assert definition.defaults == {"angle": 0.32, "height": 1.0}

    def test_definition_with_modifiers(self):
        """Test creating definition with modifiers."""
        definition = WorkflowDefinition(
            name="test_workflow",
            description="Test",
            steps=[],
            modifiers={
                "straight": {"angle": 0},
                "angled": {"angle": 0.32},
            },
        )

        assert "straight" in definition.modifiers
        assert definition.modifiers["straight"] == {"angle": 0}

    def test_to_dict_includes_defaults(self):
        """Test that to_dict includes defaults."""
        definition = WorkflowDefinition(
            name="test_workflow",
            description="Test",
            steps=[],
            defaults={"var": 1},
        )

        result = definition.to_dict()

        assert "defaults" in result
        assert result["defaults"] == {"var": 1}

    def test_to_dict_includes_modifiers(self):
        """Test that to_dict includes modifiers."""
        definition = WorkflowDefinition(
            name="test_workflow",
            description="Test",
            steps=[],
            modifiers={"key": {"var": 1}},
        )

        result = definition.to_dict()

        assert "modifiers" in result
        assert result["modifiers"] == {"key": {"var": 1}}

    def test_to_dict_empty_defaults_not_included(self):
        """Test that empty defaults are not in to_dict."""
        definition = WorkflowDefinition(
            name="test_workflow",
            description="Test",
            steps=[],
        )

        result = definition.to_dict()

        assert "defaults" not in result
        assert "modifiers" not in result


class TestRegistryModifierIntegration:
    """Tests for registry integration with modifiers."""

    @pytest.fixture
    def registry_with_workflow(self):
        """Create registry with test workflow."""
        registry = get_workflow_registry()

        # Register a workflow with defaults and modifiers
        definition = WorkflowDefinition(
            name="test_parametric_workflow",
            description="Test workflow with parametric variables",
            steps=[
                WorkflowStep(
                    tool="modeling_transform_object",
                    params={
                        "name": "Leg",
                        "rotation": [0, "$angle", 0],
                    },
                ),
            ],
            defaults={"angle": 0.32},
            modifiers={
                "straight": {"angle": 0},
                "angled": {"angle": 0.32},
            },
        )
        registry.register_definition(definition)
        return registry

    def test_expand_with_default_variables(self, registry_with_workflow):
        """Test expansion uses default values."""
        calls = registry_with_workflow.expand_workflow(
            "test_parametric_workflow",
            params={},
            user_prompt="create a table",
        )

        assert len(calls) == 1
        # Should use default angle (0.32)
        assert calls[0].params["rotation"] == [0, 0.32, 0]

    def test_expand_with_modifier_override(self, registry_with_workflow):
        """Test expansion with modifier override."""
        calls = registry_with_workflow.expand_workflow(
            "test_parametric_workflow",
            params={},
            user_prompt="create a table with straight legs",
        )

        assert len(calls) == 1
        # Should use modified angle (0)
        assert calls[0].params["rotation"] == [0, 0, 0]

    def test_expand_without_user_prompt(self, registry_with_workflow):
        """Test expansion without user prompt uses defaults."""
        calls = registry_with_workflow.expand_workflow(
            "test_parametric_workflow",
            params={},
            user_prompt=None,
        )

        assert len(calls) == 1
        # Should use default angle (0.32)
        assert calls[0].params["rotation"] == [0, 0.32, 0]

    def test_params_override_modifiers(self, registry_with_workflow):
        """Test that explicit params override modifier values."""
        calls = registry_with_workflow.expand_workflow(
            "test_parametric_workflow",
            params={"angle": 0.5},  # Explicit override
            user_prompt="table with straight legs",  # Would set angle=0
        )

        assert len(calls) == 1
        # Explicit params should win
        assert calls[0].params["rotation"] == [0, 0.5, 0]


class TestPicnicTableWorkflow:
    """Tests for picnic table workflow with parametric legs."""

    @pytest.fixture
    def registry(self):
        """Get registry with picnic table workflow loaded."""
        registry = get_workflow_registry()
        registry.load_custom_workflows(reload=True)
        return registry

    def test_picnic_table_has_defaults(self, registry):
        """Test picnic table workflow has defaults defined."""
        definition = registry.get_definition("picnic_table_workflow")

        assert definition is not None
        assert definition.defaults is not None
        assert "leg_angle_left" in definition.defaults
        assert "leg_angle_right" in definition.defaults

    def test_picnic_table_has_modifiers(self, registry):
        """Test picnic table workflow has modifiers defined."""
        definition = registry.get_definition("picnic_table_workflow")

        assert definition is not None
        assert definition.modifiers is not None
        assert "straight legs" in definition.modifiers
        # YAML keeps semantic keys in English; multilingual prompts are handled via embeddings.

    def test_picnic_table_straight_legs_modifier(self, registry):
        """Test that 'straight legs' modifier sets angle to 0."""
        definition = registry.get_definition("picnic_table_workflow")

        straight_modifier = definition.modifiers.get("straight legs")

        assert straight_modifier is not None
        assert straight_modifier["leg_angle_left"] == 0
        assert straight_modifier["leg_angle_right"] == 0

    def test_picnic_table_default_is_angled(self, registry):
        """Test that default values are A-frame angled legs."""
        definition = registry.get_definition("picnic_table_workflow")

        assert definition.defaults["leg_angle_left"] == 0.32
        assert definition.defaults["leg_angle_right"] == -0.32

    def test_leg_steps_use_variables(self, registry):
        """Test that leg transformation steps use $variables."""
        definition = registry.get_definition("picnic_table_workflow")

        # Find leg transformation steps
        leg_steps = [
            s for s in definition.steps
            if s.tool == "modeling_transform_object" and "Leg_" in str(s.params.get("name", ""))
        ]

        assert len(leg_steps) > 0

        # Check that rotation uses $variable
        for step in leg_steps:
            rotation = step.params.get("rotation", [])
            # At least one element should be a $variable
            has_variable = any(
                isinstance(v, str) and v.startswith("$")
                for v in rotation
            )
            assert has_variable, f"Step for {step.params.get('name')} should use $variable in rotation"
