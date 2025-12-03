"""
Tests for Proportion Resolver.

TASK-041-13
"""

import pytest
from server.router.application.evaluator.proportion_resolver import ProportionResolver


class TestProportionResolverInit:
    """Test resolver initialization."""

    def test_init_no_dimensions(self):
        resolver = ProportionResolver()
        assert resolver.get_dimensions() is None

    def test_set_dimensions(self):
        resolver = ProportionResolver()
        resolver.set_dimensions([2.0, 4.0, 0.5])

        dims = resolver.get_dimensions()
        assert dims == [2.0, 4.0, 0.5]

    def test_set_dimensions_copies_list(self):
        """Ensure dimensions are copied, not referenced."""
        resolver = ProportionResolver()
        original = [2.0, 4.0, 0.5]
        resolver.set_dimensions(original)

        original[0] = 999.0
        assert resolver.get_dimensions()[0] == 2.0

    def test_set_dimensions_truncates(self):
        """Ensure only first 3 dimensions are used."""
        resolver = ProportionResolver()
        resolver.set_dimensions([1.0, 2.0, 3.0, 4.0, 5.0])

        dims = resolver.get_dimensions()
        assert len(dims) == 3
        assert dims == [1.0, 2.0, 3.0]

    def test_set_invalid_dimensions(self):
        resolver = ProportionResolver()
        resolver.set_dimensions([1.0])  # Too short

        assert resolver.get_dimensions() is None

    def test_clear_dimensions(self):
        resolver = ProportionResolver()
        resolver.set_dimensions([2.0, 4.0, 0.5])
        resolver.clear_dimensions()

        assert resolver.get_dimensions() is None


class TestBevelParams:
    """Test $AUTO_BEVEL* parameters."""

    @pytest.fixture
    def resolver(self):
        r = ProportionResolver()
        r.set_dimensions([2.0, 4.0, 0.5])  # min = 0.5
        return r

    def test_auto_bevel(self, resolver):
        result = resolver.resolve("$AUTO_BEVEL")
        assert result == pytest.approx(0.025)  # 5% of 0.5

    def test_auto_bevel_small(self, resolver):
        result = resolver.resolve("$AUTO_BEVEL_SMALL")
        assert result == pytest.approx(0.01)  # 2% of 0.5

    def test_auto_bevel_large(self, resolver):
        result = resolver.resolve("$AUTO_BEVEL_LARGE")
        assert result == pytest.approx(0.05)  # 10% of 0.5


class TestInsetParams:
    """Test $AUTO_INSET* parameters."""

    @pytest.fixture
    def resolver(self):
        r = ProportionResolver()
        r.set_dimensions([2.0, 4.0, 0.5])  # XY min = 2.0
        return r

    def test_auto_inset(self, resolver):
        result = resolver.resolve("$AUTO_INSET")
        assert result == pytest.approx(0.06)  # 3% of 2.0

    def test_auto_inset_thick(self, resolver):
        result = resolver.resolve("$AUTO_INSET_THICK")
        assert result == pytest.approx(0.10)  # 5% of 2.0


class TestExtrudeParams:
    """Test $AUTO_EXTRUDE* parameters."""

    @pytest.fixture
    def resolver(self):
        r = ProportionResolver()
        r.set_dimensions([2.0, 4.0, 0.5])  # Z = 0.5
        return r

    def test_auto_extrude(self, resolver):
        result = resolver.resolve("$AUTO_EXTRUDE")
        assert result == pytest.approx(0.05)  # 10% of 0.5

    def test_auto_extrude_small(self, resolver):
        result = resolver.resolve("$AUTO_EXTRUDE_SMALL")
        assert result == pytest.approx(0.025)  # 5% of 0.5

    def test_auto_extrude_deep(self, resolver):
        result = resolver.resolve("$AUTO_EXTRUDE_DEEP")
        assert result == pytest.approx(0.10)  # 20% of 0.5

    def test_auto_extrude_neg(self, resolver):
        result = resolver.resolve("$AUTO_EXTRUDE_NEG")
        assert result == pytest.approx(-0.05)  # -10% of 0.5


class TestScaleParams:
    """Test $AUTO_SCALE* parameters."""

    @pytest.fixture
    def resolver(self):
        r = ProportionResolver()
        r.set_dimensions([2.0, 4.0, 0.5])
        return r

    def test_auto_scale_small(self, resolver):
        result = resolver.resolve("$AUTO_SCALE_SMALL")
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0] == pytest.approx(1.6)   # 80% of 2.0
        assert result[1] == pytest.approx(3.2)   # 80% of 4.0
        assert result[2] == pytest.approx(0.4)   # 80% of 0.5

    def test_auto_scale_tiny(self, resolver):
        result = resolver.resolve("$AUTO_SCALE_TINY")
        assert isinstance(result, list)
        assert result[0] == pytest.approx(1.0)   # 50% of 2.0
        assert result[1] == pytest.approx(2.0)   # 50% of 4.0
        assert result[2] == pytest.approx(0.25)  # 50% of 0.5


class TestOtherParams:
    """Test other $AUTO_* parameters."""

    @pytest.fixture
    def resolver(self):
        r = ProportionResolver()
        r.set_dimensions([2.0, 4.0, 0.5])
        return r

    def test_auto_offset(self, resolver):
        result = resolver.resolve("$AUTO_OFFSET")
        assert result == pytest.approx(0.01)  # 2% of 0.5 (min)

    def test_auto_thickness(self, resolver):
        result = resolver.resolve("$AUTO_THICKNESS")
        assert result == pytest.approx(0.025)  # 5% of 0.5 (Z)

    def test_auto_screen_depth(self, resolver):
        result = resolver.resolve("$AUTO_SCREEN_DEPTH")
        assert result == pytest.approx(0.25)  # 50% of 0.5

    def test_auto_screen_depth_neg(self, resolver):
        result = resolver.resolve("$AUTO_SCREEN_DEPTH_NEG")
        assert result == pytest.approx(-0.25)  # -50% of 0.5

    def test_auto_loop_pos(self, resolver):
        result = resolver.resolve("$AUTO_LOOP_POS")
        assert result == pytest.approx(0.8)


class TestResolvePassthrough:
    """Test values that should pass through unchanged."""

    @pytest.fixture
    def resolver(self):
        r = ProportionResolver()
        r.set_dimensions([2.0, 4.0, 0.5])
        return r

    def test_number_passthrough(self, resolver):
        assert resolver.resolve(42) == 42
        assert resolver.resolve(3.14) == pytest.approx(3.14)

    def test_string_passthrough(self, resolver):
        assert resolver.resolve("plain string") == "plain string"
        assert resolver.resolve("CUBE") == "CUBE"

    def test_none_passthrough(self, resolver):
        assert resolver.resolve(None) is None

    def test_bool_passthrough(self, resolver):
        assert resolver.resolve(True) is True
        assert resolver.resolve(False) is False

    def test_dollar_non_auto_passthrough(self, resolver):
        """$CALCULATE and other $ prefixes should pass through."""
        assert resolver.resolve("$CALCULATE(width * 0.5)") == "$CALCULATE(width * 0.5)"
        assert resolver.resolve("$width") == "$width"


class TestResolveRecursive:
    """Test recursive resolution in lists and dicts."""

    @pytest.fixture
    def resolver(self):
        r = ProportionResolver()
        r.set_dimensions([2.0, 4.0, 0.5])  # min=0.5, Z=0.5
        return r

    def test_resolve_list(self, resolver):
        result = resolver.resolve(["$AUTO_BEVEL", 1.0, "$AUTO_INSET"])
        assert result[0] == pytest.approx(0.025)  # AUTO_BEVEL
        assert result[1] == 1.0
        assert result[2] == pytest.approx(0.06)   # AUTO_INSET

    def test_resolve_dict(self, resolver):
        result = resolver.resolve({
            "width": "$AUTO_BEVEL",
            "segments": 3,
        })
        assert result["width"] == pytest.approx(0.025)
        assert result["segments"] == 3

    def test_resolve_nested(self, resolver):
        result = resolver.resolve({
            "scale": ["$AUTO_SCALE_SMALL"],
            "offset": "$AUTO_OFFSET",
        })
        # scale contains a list with one AUTO_SCALE_SMALL
        # but AUTO_SCALE_SMALL itself returns a list
        # so we get a list containing a list
        assert result["offset"] == pytest.approx(0.01)


class TestResolveParams:
    """Test resolve_params method."""

    @pytest.fixture
    def resolver(self):
        r = ProportionResolver()
        r.set_dimensions([2.0, 4.0, 0.5])
        return r

    def test_resolve_params_basic(self, resolver):
        params = {
            "width": "$AUTO_BEVEL",
            "segments": 3,
            "mode": "EDIT",
        }
        resolved = resolver.resolve_params(params)

        assert resolved["width"] == pytest.approx(0.025)
        assert resolved["segments"] == 3
        assert resolved["mode"] == "EDIT"

    def test_resolve_params_with_list(self, resolver):
        params = {
            "move": [0, 0, "$AUTO_EXTRUDE_NEG"],
        }
        resolved = resolver.resolve_params(params)

        assert resolved["move"][0] == 0
        assert resolved["move"][1] == 0
        assert resolved["move"][2] == pytest.approx(-0.05)


class TestNoDimensions:
    """Test behavior when no dimensions are set."""

    def test_resolve_without_dimensions(self):
        resolver = ProportionResolver()
        # No dimensions set

        result = resolver.resolve("$AUTO_BEVEL")
        # Should return original value
        assert result == "$AUTO_BEVEL"

    def test_resolve_params_without_dimensions(self):
        resolver = ProportionResolver()

        params = {"width": "$AUTO_BEVEL", "count": 5}
        resolved = resolver.resolve_params(params)

        assert resolved["width"] == "$AUTO_BEVEL"  # Unchanged
        assert resolved["count"] == 5


class TestUnknownParams:
    """Test unknown $AUTO_* parameters."""

    @pytest.fixture
    def resolver(self):
        r = ProportionResolver()
        r.set_dimensions([2.0, 4.0, 0.5])
        return r

    def test_unknown_auto_param(self, resolver):
        result = resolver.resolve("$AUTO_UNKNOWN")
        assert result == "$AUTO_UNKNOWN"  # Unchanged


class TestIsAutoParam:
    """Test is_auto_param helper method."""

    def test_is_auto_param_true(self):
        resolver = ProportionResolver()
        assert resolver.is_auto_param("$AUTO_BEVEL") is True
        assert resolver.is_auto_param("$AUTO_UNKNOWN") is True

    def test_is_auto_param_false(self):
        resolver = ProportionResolver()
        assert resolver.is_auto_param("plain") is False
        assert resolver.is_auto_param("$CALCULATE(x)") is False
        assert resolver.is_auto_param(42) is False
        assert resolver.is_auto_param(None) is False


class TestGetAvailableParams:
    """Test get_available_params method."""

    def test_returns_list(self):
        resolver = ProportionResolver()
        params = resolver.get_available_params()

        assert isinstance(params, list)
        assert len(params) > 0

    def test_params_have_name_and_description(self):
        resolver = ProportionResolver()
        params = resolver.get_available_params()

        for param in params:
            assert "name" in param
            assert "description" in param
            assert param["name"].startswith("$AUTO_")


class TestRealWorldExamples:
    """Test real-world workflow parameter examples."""

    def test_phone_workflow_params(self):
        """Test parameters for phone workflow."""
        resolver = ProportionResolver()
        # Typical phone proportions
        resolver.set_dimensions([0.07, 0.15, 0.008])  # 7cm x 15cm x 8mm

        bevel = resolver.resolve("$AUTO_BEVEL")
        assert bevel == pytest.approx(0.0004)  # 5% of 8mm

        screen_depth = resolver.resolve("$AUTO_SCREEN_DEPTH_NEG")
        assert screen_depth == pytest.approx(-0.004)  # -50% of 8mm

    def test_table_workflow_params(self):
        """Test parameters for table workflow."""
        resolver = ProportionResolver()
        # Typical table proportions
        resolver.set_dimensions([1.2, 0.8, 0.75])  # 1.2m x 0.8m x 0.75m

        bevel = resolver.resolve("$AUTO_BEVEL")
        assert bevel == pytest.approx(0.0375)  # 5% of 0.75m

        extrude = resolver.resolve("$AUTO_EXTRUDE")
        assert extrude == pytest.approx(0.075)  # 10% of 0.75m

    def test_tower_workflow_params(self):
        """Test parameters for tower workflow."""
        resolver = ProportionResolver()
        # Tall tower proportions
        resolver.set_dimensions([1.0, 1.0, 5.0])  # 1m x 1m x 5m

        bevel = resolver.resolve("$AUTO_BEVEL")
        assert bevel == pytest.approx(0.05)  # 5% of 1.0m (min)

        inset = resolver.resolve("$AUTO_INSET")
        assert inset == pytest.approx(0.03)  # 3% of 1.0m (XY min)
