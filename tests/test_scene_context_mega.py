"""Tests for scene_context mega tool routing and validation."""
import pytest
from unittest.mock import MagicMock, patch


class TestSceneContextMega:
    """Test scene_context mega tool routing."""

    def setup_method(self):
        self.mock_ctx = MagicMock()

    @patch("server.adapters.mcp.areas.scene._scene_get_mode")
    def test_action_mode_routes_to_get_mode(self, mock_get_mode):
        """Test action='mode' routes to _scene_get_mode."""
        from server.adapters.mcp.areas.scene import scene_context

        mock_get_mode.return_value = "Mode result"
        # Access underlying function from FunctionTool
        result = scene_context.fn(self.mock_ctx, action="mode")

        mock_get_mode.assert_called_once_with(self.mock_ctx)
        assert result == "Mode result"

    @patch("server.adapters.mcp.areas.scene._scene_list_selection")
    def test_action_selection_routes_to_list_selection(self, mock_list_selection):
        """Test action='selection' routes to _scene_list_selection."""
        from server.adapters.mcp.areas.scene import scene_context

        mock_list_selection.return_value = "Selection result"
        result = scene_context.fn(self.mock_ctx, action="selection")

        mock_list_selection.assert_called_once_with(self.mock_ctx)
        assert result == "Selection result"

    def test_invalid_action_returns_error(self):
        """Test invalid action returns helpful error message."""
        from server.adapters.mcp.areas.scene import scene_context

        result = scene_context.fn(self.mock_ctx, action="invalid")

        assert "Unknown action" in result
        assert "invalid" in result
        assert "mode" in result
        assert "selection" in result
