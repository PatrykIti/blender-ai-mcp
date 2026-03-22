"""Tests for scene_context mega tool routing and validation."""
import pytest
from unittest.mock import MagicMock, patch

from server.adapters.mcp.contracts.scene import SceneContextResponseContract


class TestSceneContextMega:
    """Test scene_context mega tool routing."""

    def setup_method(self):
        self.mock_ctx = MagicMock()

    @patch("server.adapters.mcp.areas.scene._scene_get_mode")
    def test_action_mode_routes_to_get_mode(self, mock_get_mode):
        """Test action='mode' routes to _scene_get_mode."""
        from server.adapters.mcp.areas.scene import scene_context

        callable_scene_context = getattr(scene_context, "fn", scene_context)
        mock_get_mode.return_value = {
            "mode": "OBJECT",
            "active_object": "Cube",
            "active_object_type": "MESH",
            "selected_object_names": ["Cube"],
            "selection_count": 1,
        }
        # Access underlying function from FunctionTool
        result = callable_scene_context(self.mock_ctx, action="mode")

        mock_get_mode.assert_called_once_with(self.mock_ctx)
        assert isinstance(result, SceneContextResponseContract)
        assert result.action == "mode"
        assert result.payload.mode == "OBJECT"

    @patch("server.adapters.mcp.areas.scene._scene_list_selection")
    def test_action_selection_routes_to_list_selection(self, mock_list_selection):
        """Test action='selection' routes to _scene_list_selection."""
        from server.adapters.mcp.areas.scene import scene_context

        callable_scene_context = getattr(scene_context, "fn", scene_context)
        mock_list_selection.return_value = {
            "mode": "EDIT",
            "selected_object_names": ["Cube"],
            "selection_count": 1,
            "edit_mode_vertex_count": 8,
            "edit_mode_edge_count": 12,
            "edit_mode_face_count": 6,
        }
        result = callable_scene_context(self.mock_ctx, action="selection")

        mock_list_selection.assert_called_once_with(self.mock_ctx)
        assert isinstance(result, SceneContextResponseContract)
        assert result.action == "selection"
        assert result.payload.mode == "EDIT"

    def test_invalid_action_returns_error(self):
        """Test invalid action returns helpful error message."""
        from server.adapters.mcp.areas.scene import scene_context

        callable_scene_context = getattr(scene_context, "fn", scene_context)
        result = callable_scene_context(self.mock_ctx, action="invalid")

        assert isinstance(result, SceneContextResponseContract)
        assert "Unknown action" in result.error
        assert "invalid" in result.error
        assert "mode" in result.error
        assert "selection" in result.error
