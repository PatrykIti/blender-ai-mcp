"""
Unit tests for Proportion Calculator.

Tests for proportion calculation utilities.
"""

import pytest

from server.router.application.analyzers.proportion_calculator import (
    calculate_proportions,
    get_proportion_summary,
    is_phone_like_proportions,
    is_tower_like_proportions,
    is_table_like_proportions,
    is_wheel_like_proportions,
    get_dimensions_from_dict,
)
from server.router.domain.entities.scene_context import ProportionInfo


class TestCalculateProportions:
    """Test calculate_proportions function."""

    def test_cubic_dimensions(self):
        """Test proportions for a cube."""
        props = calculate_proportions([1.0, 1.0, 1.0])

        assert props.aspect_xy == 1.0
        assert props.aspect_xz == 1.0
        assert props.aspect_yz == 1.0
        assert props.is_cubic is True
        assert props.is_flat is False
        assert props.is_tall is False

    def test_flat_dimensions(self):
        """Test proportions for a flat object."""
        # z is much smaller than x and y
        props = calculate_proportions([2.0, 2.0, 0.1])

        assert props.is_flat is True
        assert props.is_tall is False

    def test_tall_dimensions(self):
        """Test proportions for a tall object."""
        # z is much larger than x and y
        props = calculate_proportions([0.5, 0.5, 3.0])

        assert props.is_tall is True
        assert props.is_flat is False

    def test_wide_dimensions(self):
        """Test proportions for a wide object."""
        # x is much larger than y and z
        props = calculate_proportions([5.0, 1.0, 1.0])

        assert props.is_wide is True

    def test_dominant_axis_x(self):
        """Test dominant axis detection for x."""
        props = calculate_proportions([3.0, 1.0, 2.0])

        assert props.dominant_axis == "x"

    def test_dominant_axis_y(self):
        """Test dominant axis detection for y."""
        props = calculate_proportions([1.0, 3.0, 2.0])

        assert props.dominant_axis == "y"

    def test_dominant_axis_z(self):
        """Test dominant axis detection for z."""
        props = calculate_proportions([1.0, 2.0, 3.0])

        assert props.dominant_axis == "z"

    def test_volume_calculation(self):
        """Test volume calculation."""
        props = calculate_proportions([2.0, 3.0, 4.0])

        assert props.volume == 24.0

    def test_surface_area_calculation(self):
        """Test surface area calculation."""
        props = calculate_proportions([1.0, 1.0, 1.0])

        # 2 * (1*1 + 1*1 + 1*1) = 6
        assert props.surface_area == 6.0

    def test_empty_dimensions(self):
        """Test with empty dimensions."""
        props = calculate_proportions([])

        assert isinstance(props, ProportionInfo)

    def test_near_zero_dimensions(self):
        """Test with near-zero dimensions (avoids division by zero)."""
        props = calculate_proportions([0.0001, 0.0001, 0.0001])

        assert props.aspect_xy == 1.0
        assert props.is_cubic is True


class TestProportionSummary:
    """Test get_proportion_summary function."""

    def test_flat_summary(self):
        """Test summary for flat object."""
        props = calculate_proportions([2.0, 2.0, 0.1])

        summary = get_proportion_summary(props)

        assert "flat" in summary

    def test_tall_summary(self):
        """Test summary for tall object."""
        props = calculate_proportions([0.3, 0.3, 2.0])

        summary = get_proportion_summary(props)

        assert "tall" in summary

    def test_cubic_summary(self):
        """Test summary for cubic object."""
        props = calculate_proportions([1.0, 1.0, 1.0])

        summary = get_proportion_summary(props)

        assert "cubic" in summary

    def test_combined_summary(self):
        """Test summary with multiple descriptors."""
        # Flat and wide
        props = calculate_proportions([5.0, 1.0, 0.1])

        summary = get_proportion_summary(props)

        assert "flat" in summary
        assert "wide" in summary


class TestPhoneLikeProportions:
    """Test is_phone_like_proportions function."""

    def test_phone_like_shape(self):
        """Test detection of phone-like proportions."""
        # Typical phone: 0.4 x 0.8 x 0.05
        props = calculate_proportions([0.4, 0.8, 0.05])

        assert is_phone_like_proportions(props) is True

    def test_not_phone_like_cube(self):
        """Test cube is not phone-like."""
        props = calculate_proportions([1.0, 1.0, 1.0])

        assert is_phone_like_proportions(props) is False

    def test_not_phone_like_too_tall(self):
        """Test tall object is not phone-like."""
        props = calculate_proportions([0.4, 0.8, 2.0])

        assert is_phone_like_proportions(props) is False


class TestTowerLikeProportions:
    """Test is_tower_like_proportions function."""

    def test_tower_like_shape(self):
        """Test detection of tower-like proportions."""
        # Tower: tall with small base
        props = calculate_proportions([0.3, 0.3, 3.0])

        assert is_tower_like_proportions(props) is True

    def test_not_tower_like_cube(self):
        """Test cube is not tower-like."""
        props = calculate_proportions([1.0, 1.0, 1.0])

        assert is_tower_like_proportions(props) is False


class TestTableLikeProportions:
    """Test is_table_like_proportions function."""

    def test_table_like_shape(self):
        """Test detection of table-like proportions."""
        # Table: flat surface
        props = calculate_proportions([2.0, 1.5, 0.1])

        assert is_table_like_proportions(props) is True

    def test_not_table_like_tall(self):
        """Test tall object is not table-like."""
        props = calculate_proportions([1.0, 1.0, 5.0])

        assert is_table_like_proportions(props) is False


class TestWheelLikeProportions:
    """Test is_wheel_like_proportions function."""

    def test_wheel_like_shape(self):
        """Test detection of wheel-like proportions."""
        # Wheel: circular and flat
        props = calculate_proportions([1.0, 1.0, 0.1])

        assert is_wheel_like_proportions(props) is True

    def test_not_wheel_like_rectangular(self):
        """Test rectangular object is not wheel-like."""
        props = calculate_proportions([2.0, 1.0, 0.1])

        assert is_wheel_like_proportions(props) is False


class TestGetDimensionsFromDict:
    """Test get_dimensions_from_dict function."""

    def test_dimensions_list(self):
        """Test extracting dimensions as list."""
        data = {"dimensions": [1.0, 2.0, 3.0]}

        dims = get_dimensions_from_dict(data)

        assert dims == [1.0, 2.0, 3.0]

    def test_dimensions_tuple(self):
        """Test extracting dimensions as tuple."""
        data = {"dimensions": (1.0, 2.0, 3.0)}

        dims = get_dimensions_from_dict(data)

        assert dims == [1.0, 2.0, 3.0]

    def test_dimensions_dict(self):
        """Test extracting dimensions as dict."""
        data = {"dimensions": {"x": 1.0, "y": 2.0, "z": 3.0}}

        dims = get_dimensions_from_dict(data)

        assert dims == [1.0, 2.0, 3.0]

    def test_xyz_keys(self):
        """Test extracting x, y, z directly."""
        data = {"x": 1.0, "y": 2.0, "z": 3.0}

        dims = get_dimensions_from_dict(data)

        assert dims == [1.0, 2.0, 3.0]

    def test_size_key(self):
        """Test extracting from size key."""
        data = {"size": [1.0, 2.0, 3.0]}

        dims = get_dimensions_from_dict(data)

        assert dims == [1.0, 2.0, 3.0]

    def test_empty_dict(self):
        """Test with empty dict."""
        dims = get_dimensions_from_dict({})

        assert dims is None

    def test_no_dimensions(self):
        """Test with dict without dimensions."""
        data = {"name": "Cube", "type": "MESH"}

        dims = get_dimensions_from_dict(data)

        assert dims is None
