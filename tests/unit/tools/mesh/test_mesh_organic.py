"""
Tests for TASK-038-5 (Proportional Editing).
Pure pytest style - uses conftest.py fixtures.
"""
import sys
import pytest
from unittest.mock import MagicMock

# conftest.py handles bpy mocking
from blender_addon.application.handlers.mesh import MeshHandler


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mesh_handler():
    """Provides a fresh MeshHandler instance."""
    return MeshHandler()


@pytest.fixture
def mock_tool_settings():
    """Sets up mock tool settings for proportional editing."""
    mock_bpy = sys.modules["bpy"]

    mock_settings = MagicMock()
    mock_settings.proportional_edit = 'DISABLED'
    mock_settings.proportional_edit_falloff = 'SMOOTH'
    mock_settings.proportional_size = 1.0

    mock_bpy.context.tool_settings = mock_settings
    return mock_settings


# =============================================================================
# TASK-038-5: Proportional Editing Tests
# =============================================================================

class TestSetProportionalEdit:
    """Tests for mesh_set_proportional_edit tool."""

    def test_enable_proportional_edit_default(self, mesh_handler, mock_tool_settings):
        """Should enable proportional editing with default parameters."""
        result = mesh_handler.set_proportional_edit(enabled=True)

        assert mock_tool_settings.proportional_edit == 'ENABLED'
        assert mock_tool_settings.proportional_edit_falloff == 'SMOOTH'
        assert mock_tool_settings.proportional_size == 1.0
        assert "enabled" in result.lower()

    def test_enable_proportional_edit_with_options(self, mesh_handler, mock_tool_settings):
        """Should enable proportional editing with custom options."""
        result = mesh_handler.set_proportional_edit(
            enabled=True,
            falloff_type="SHARP",
            size=2.0,
            use_connected=False
        )

        assert mock_tool_settings.proportional_edit == 'ENABLED'
        assert mock_tool_settings.proportional_edit_falloff == 'SHARP'
        assert mock_tool_settings.proportional_size == 2.0
        assert "SHARP" in result

    def test_enable_proportional_edit_connected(self, mesh_handler, mock_tool_settings):
        """Should enable proportional editing with connected mode."""
        result = mesh_handler.set_proportional_edit(
            enabled=True,
            use_connected=True
        )

        assert mock_tool_settings.proportional_edit == 'CONNECTED'
        assert "connected" in result.lower()

    def test_disable_proportional_edit(self, mesh_handler, mock_tool_settings):
        """Should disable proportional editing."""
        mock_tool_settings.proportional_edit = 'ENABLED'

        result = mesh_handler.set_proportional_edit(enabled=False)

        assert mock_tool_settings.proportional_edit == 'DISABLED'
        assert "disabled" in result.lower()

    def test_proportional_edit_all_falloff_types(self, mesh_handler, mock_tool_settings):
        """Should accept all valid falloff types."""
        valid_falloffs = [
            "SMOOTH", "SPHERE", "ROOT", "INVERSE_SQUARE",
            "SHARP", "LINEAR", "CONSTANT", "RANDOM"
        ]

        for falloff in valid_falloffs:
            result = mesh_handler.set_proportional_edit(
                enabled=True,
                falloff_type=falloff
            )
            assert mock_tool_settings.proportional_edit_falloff == falloff
            assert falloff in result

    def test_proportional_edit_invalid_falloff_raises(self, mesh_handler, mock_tool_settings):
        """Should raise ValueError for invalid falloff type."""
        with pytest.raises(ValueError, match="Invalid falloff type"):
            mesh_handler.set_proportional_edit(falloff_type="INVALID")

    def test_proportional_edit_case_insensitive_falloff(self, mesh_handler, mock_tool_settings):
        """Should accept lowercase falloff types."""
        result = mesh_handler.set_proportional_edit(
            enabled=True,
            falloff_type="smooth"  # lowercase
        )

        assert mock_tool_settings.proportional_edit_falloff == "SMOOTH"
        assert "SMOOTH" in result

    def test_proportional_edit_clamps_size(self, mesh_handler, mock_tool_settings):
        """Should clamp size to minimum value."""
        mesh_handler.set_proportional_edit(enabled=True, size=-5.0)

        # Should be clamped to minimum of 0.001
        assert mock_tool_settings.proportional_size >= 0.001

    def test_proportional_edit_size_zero_clamped(self, mesh_handler, mock_tool_settings):
        """Should clamp size of 0 to minimum."""
        mesh_handler.set_proportional_edit(enabled=True, size=0.0)

        assert mock_tool_settings.proportional_size == 0.001

    def test_proportional_edit_large_size(self, mesh_handler, mock_tool_settings):
        """Should accept large size values."""
        mesh_handler.set_proportional_edit(enabled=True, size=100.0)

        assert mock_tool_settings.proportional_size == 100.0
