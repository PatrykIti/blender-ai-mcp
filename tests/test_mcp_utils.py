"""Tests for MCP adapter utilities."""
import pytest
from server.adapters.mcp.utils import parse_coordinate, parse_dict


class TestParseCoordinate:
    """Test coordinate parsing utility function."""

    def test_parse_string_with_floats(self):
        """Should parse JSON string with floats."""
        result = parse_coordinate('[0.0, 0.0, 2.0]')
        assert result == [0.0, 0.0, 2.0]

    def test_parse_string_with_integers(self):
        """Should parse JSON string with integers and convert to floats."""
        result = parse_coordinate('[1, 2, 3]')
        assert result == [1.0, 2.0, 3.0]

    def test_parse_string_with_negative_values(self):
        """Should parse JSON string with negative values."""
        result = parse_coordinate('[-1.5, 2.5, -3.0]')
        assert result == [-1.5, 2.5, -3.0]

    def test_parse_list_directly(self):
        """Should handle list input without parsing."""
        result = parse_coordinate([0.0, 0.0, 2.0])
        assert result == [0.0, 0.0, 2.0]

    def test_parse_list_with_integers(self):
        """Should convert integer list elements to floats."""
        result = parse_coordinate([1, 2, 3])
        assert result == [1.0, 2.0, 3.0]

    def test_parse_none(self):
        """Should return None when input is None."""
        result = parse_coordinate(None)
        assert result is None

    def test_parse_invalid_string(self):
        """Should raise ValueError for invalid JSON string."""
        with pytest.raises(ValueError, match="Invalid coordinate format"):
            parse_coordinate("invalid")

    def test_parse_string_not_list(self):
        """Should raise ValueError when JSON string doesn't contain a list."""
        with pytest.raises(ValueError, match="Expected a list"):
            parse_coordinate('{"x": 1, "y": 2}')

    def test_parse_empty_string(self):
        """Should raise ValueError for empty string."""
        with pytest.raises(ValueError, match="Invalid coordinate format"):
            parse_coordinate("")

    def test_parse_tuple(self):
        """Should handle tuple input and convert to list of floats."""
        result = parse_coordinate((1, 2, 3))
        assert result == [1.0, 2.0, 3.0]


class TestParseDict:
    """Test dictionary parsing utility function."""

    def test_parse_string_with_dict(self):
        """Should parse JSON string with dict."""
        result = parse_dict('{"levels": 2}')
        assert result == {"levels": 2}

    def test_parse_string_with_multiple_keys(self):
        """Should parse JSON string with multiple keys."""
        result = parse_dict('{"levels": 2, "render_levels": 3}')
        assert result == {"levels": 2, "render_levels": 3}

    def test_parse_string_with_nested_dict(self):
        """Should parse JSON string with nested dict."""
        result = parse_dict('{"outer": {"inner": "value"}}')
        assert result == {"outer": {"inner": "value"}}

    def test_parse_dict_directly(self):
        """Should handle dict input without parsing."""
        result = parse_dict({"levels": 2})
        assert result == {"levels": 2}

    def test_parse_none(self):
        """Should return None when input is None."""
        result = parse_dict(None)
        assert result is None

    def test_parse_invalid_string(self):
        """Should raise ValueError for invalid JSON string."""
        with pytest.raises(ValueError, match="Invalid dictionary format"):
            parse_dict("invalid")

    def test_parse_string_not_dict(self):
        """Should raise ValueError when JSON string doesn't contain a dict."""
        with pytest.raises(ValueError, match="Expected a dictionary"):
            parse_dict('[1, 2, 3]')

    def test_parse_empty_string(self):
        """Should raise ValueError for empty string."""
        with pytest.raises(ValueError, match="Invalid dictionary format"):
            parse_dict("")

    def test_parse_empty_dict(self):
        """Should handle empty dict."""
        result = parse_dict({})
        assert result == {}
