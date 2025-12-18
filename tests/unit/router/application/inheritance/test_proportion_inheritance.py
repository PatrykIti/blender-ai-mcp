"""
Tests for ProportionInheritance.

TASK-046-4
"""

import pytest
from typing import Dict, List, Tuple

from server.router.application.inheritance.proportion_inheritance import (
    ProportionInheritance,
    ProportionRule,
    InheritedProportions,
)


class TestProportionRule:
    """Tests for ProportionRule dataclass."""

    def test_create_rule(self):
        """Test creating a proportion rule."""
        rule = ProportionRule(
            name="bevel_ratio",
            value=0.04,
            source_workflow="phone_workflow",
            weight=1.0,
            description="Bevel size ratio",
        )

        assert rule.name == "bevel_ratio"
        assert rule.value == 0.04
        assert rule.source_workflow == "phone_workflow"

    def test_to_dict(self):
        """Test converting rule to dict."""
        rule = ProportionRule(
            name="bevel_ratio",
            value=0.04,
            source_workflow="phone_workflow",
        )

        d = rule.to_dict()

        assert d["name"] == "bevel_ratio"
        assert d["value"] == 0.04
        assert d["source_workflow"] == "phone_workflow"


class TestInheritedProportions:
    """Tests for InheritedProportions dataclass."""

    def test_get_existing_rule(self):
        """Test getting an existing rule value."""
        proportions = InheritedProportions()
        proportions.rules["bevel_ratio"] = ProportionRule(
            name="bevel_ratio",
            value=0.04,
            source_workflow="phone_workflow",
        )

        value = proportions.get("bevel_ratio")

        assert value == 0.04

    def test_get_missing_rule_returns_default(self):
        """Test getting a missing rule returns default."""
        proportions = InheritedProportions()

        value = proportions.get("missing_rule", default=0.1)

        assert value == 0.1

    def test_has_existing_rule(self):
        """Test has returns True for existing rule."""
        proportions = InheritedProportions()
        proportions.rules["bevel_ratio"] = ProportionRule(
            name="bevel_ratio",
            value=0.04,
            source_workflow="phone_workflow",
        )

        assert proportions.has("bevel_ratio") is True

    def test_has_missing_rule(self):
        """Test has returns False for missing rule."""
        proportions = InheritedProportions()

        assert proportions.has("missing_rule") is False

    def test_to_dict(self):
        """Test converting to simple dict."""
        proportions = InheritedProportions()
        proportions.rules["bevel_ratio"] = ProportionRule(
            name="bevel_ratio",
            value=0.04,
            source_workflow="phone_workflow",
        )
        proportions.rules["inset_ratio"] = ProportionRule(
            name="inset_ratio",
            value=0.05,
            source_workflow="phone_workflow",
        )

        d = proportions.to_dict()

        assert d["bevel_ratio"] == 0.04
        assert d["inset_ratio"] == 0.05

    def test_to_full_dict(self):
        """Test converting to full dict with metadata."""
        proportions = InheritedProportions()
        proportions.rules["bevel_ratio"] = ProportionRule(
            name="bevel_ratio",
            value=0.04,
            source_workflow="phone_workflow",
        )
        proportions.sources = ["phone_workflow"]
        proportions.total_weight = 1.0

        d = proportions.to_full_dict()

        assert "rules" in d
        assert "sources" in d
        assert "total_weight" in d
        assert d["total_weight"] == 1.0


class TestProportionInheritance:
    """Tests for ProportionInheritance class."""

    @pytest.fixture
    def inheritance(self):
        """Create ProportionInheritance instance."""
        return ProportionInheritance()

    def test_get_workflow_proportions_builtin(self, inheritance):
        """Test getting built-in workflow proportions."""
        proportions = inheritance.get_workflow_proportions("phone_workflow")

        assert "bevel_ratio" in proportions
        assert "inset_ratio" in proportions
        assert proportions["bevel_ratio"] == 0.04

    def test_get_workflow_proportions_missing(self, inheritance):
        """Test getting proportions for unknown workflow."""
        proportions = inheritance.get_workflow_proportions("unknown_workflow")

        assert proportions == {}

    def test_register_custom_proportions(self, inheritance):
        """Test registering custom proportions."""
        custom = {
            "custom_ratio": 0.1,
            "other_ratio": 0.2,
        }

        inheritance.register_proportions("custom_workflow", custom)

        proportions = inheritance.get_workflow_proportions("custom_workflow")
        assert proportions["custom_ratio"] == 0.1

    def test_custom_proportions_override_builtin(self, inheritance):
        """Test that custom proportions override built-in."""
        custom = {"bevel_ratio": 0.99}

        inheritance.register_proportions("phone_workflow", custom)

        proportions = inheritance.get_workflow_proportions("phone_workflow")
        assert proportions["bevel_ratio"] == 0.99

    def test_inherit_from_single_workflow(self, inheritance):
        """Test inheriting from a single workflow."""
        similar = [("phone_workflow", 1.0)]

        result = inheritance.inherit_proportions(similar)

        assert result.has("bevel_ratio")
        assert result.get("bevel_ratio") == 0.04
        assert "phone_workflow" in result.sources

    def test_inherit_from_empty_list(self, inheritance):
        """Test inheriting from empty list."""
        result = inheritance.inherit_proportions([])

        assert len(result.rules) == 0
        assert result.total_weight == 0.0

    def test_inherit_weighted_combination(self, inheritance):
        """Test weighted combination of proportions."""
        # phone_workflow bevel_ratio = 0.04
        # tower_workflow bevel_ratio = 0.02
        similar = [
            ("phone_workflow", 0.7),
            ("tower_workflow", 0.3),
        ]

        result = inheritance.inherit_proportions(similar)

        # Weighted average: (0.04 * 0.7 + 0.02 * 0.3) / (0.7 + 0.3) = 0.034
        expected = (0.04 * 0.7 + 0.02 * 0.3) / 1.0
        assert abs(result.get("bevel_ratio") - expected) < 0.001

    def test_inherit_total_weight(self, inheritance):
        """Test total weight is sum of similarities."""
        similar = [
            ("phone_workflow", 0.7),
            ("table_workflow", 0.5),
        ]

        result = inheritance.inherit_proportions(similar)

        assert result.total_weight == 1.2

    def test_apply_to_dimensions_bevel(self, inheritance):
        """Test applying bevel ratio to dimensions."""
        proportions = InheritedProportions()
        proportions.rules["bevel_ratio"] = ProportionRule(
            name="bevel_ratio",
            value=0.05,
            source_workflow="phone_workflow",
        )

        # Object 1m x 0.5m x 0.1m, min_dim = 0.1
        dimensions = [1.0, 0.5, 0.1]
        applied = inheritance.apply_to_dimensions(proportions, dimensions)

        # bevel = 0.05 * 0.1 = 0.005
        assert abs(applied["bevel_ratio"] - 0.005) < 0.0001

    def test_apply_to_dimensions_inset(self, inheritance):
        """Test applying inset ratio to dimensions."""
        proportions = InheritedProportions()
        proportions.rules["inset_ratio"] = ProportionRule(
            name="inset_ratio",
            value=0.1,
            source_workflow="phone_workflow",
        )

        # Object 1.0m x 0.5m x 0.1m, min_xy = 0.5
        dimensions = [1.0, 0.5, 0.1]
        applied = inheritance.apply_to_dimensions(proportions, dimensions)

        # inset = 0.1 * 0.5 = 0.05
        assert abs(applied["inset_ratio"] - 0.05) < 0.0001

    def test_apply_to_dimensions_extrude(self, inheritance):
        """Test applying extrude ratio to dimensions."""
        proportions = InheritedProportions()
        proportions.rules["extrude_ratio"] = ProportionRule(
            name="extrude_ratio",
            value=0.5,
            source_workflow="phone_workflow",
        )

        # Object with z = 2.0
        dimensions = [1.0, 1.0, 2.0]
        applied = inheritance.apply_to_dimensions(proportions, dimensions)

        # extrude = 0.5 * 2.0 = 1.0
        assert abs(applied["extrude_ratio"] - 1.0) < 0.0001

    def test_apply_to_dimensions_insufficient(self, inheritance):
        """Test applying with insufficient dimensions."""
        proportions = InheritedProportions()
        proportions.rules["bevel_ratio"] = ProportionRule(
            name="bevel_ratio",
            value=0.05,
            source_workflow="phone_workflow",
        )

        # Only 2 dimensions
        dimensions = [1.0, 0.5]
        applied = inheritance.apply_to_dimensions(proportions, dimensions)

        assert applied == {}

    def test_get_dimension_context(self, inheritance):
        """Test getting dimension context."""
        dimensions = [1.0, 0.5, 0.2]

        context = inheritance.get_dimension_context(dimensions)

        assert context["x"] == 1.0
        assert context["y"] == 0.5
        assert context["z"] == 0.2
        assert context["min_dim"] == 0.2
        assert context["max_dim"] == 1.0
        assert context["min_xy"] == 0.5
        assert abs(context["volume"] - 0.1) < 0.0001

    def test_suggest_proportions_for_object(self, inheritance):
        """Test suggesting proportions for new object type."""
        similar = [("table_workflow", 0.72), ("tower_workflow", 0.45)]
        dimensions = [0.5, 0.5, 0.9]

        suggestion = inheritance.suggest_proportions_for_object(
            "chair",
            similar,
            dimensions,
        )

        assert suggestion["object_type"] == "chair"
        assert "inherited_proportions" in suggestion
        assert "applied_values" in suggestion
        assert "sources" in suggestion

    def test_get_available_rules(self, inheritance):
        """Test getting all available rule names."""
        rules = inheritance.get_available_rules()

        assert "bevel_ratio" in rules
        assert "inset_ratio" in rules
        assert isinstance(rules, list)
        assert rules == sorted(rules)  # Should be sorted

    def test_get_info(self, inheritance):
        """Test getting inheritance system info."""
        info = inheritance.get_info()

        assert "builtin_workflows" in info
        assert "custom_workflows" in info
        assert "available_rules" in info
        assert "total_workflows" in info
        assert "phone_workflow" in info["builtin_workflows"]
