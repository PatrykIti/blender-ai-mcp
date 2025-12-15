"""Tests for MCP mesh_transform_selected vector parsing (TASK-064)."""

from unittest.mock import MagicMock, patch


class TestMeshTransformSelectedMcpParsing:
    def setup_method(self):
        self.mock_ctx = MagicMock()

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh.get_mesh_handler")
    def test_parses_string_scale_param(self, mock_get_mesh_handler, _mock_router_enabled):
        from server.adapters.mcp.areas.mesh import mesh_transform_selected

        handler = MagicMock()
        handler.transform_selected.return_value = "OK"
        mock_get_mesh_handler.return_value = handler

        result = mesh_transform_selected.fn(self.mock_ctx, scale="[1, 1, 0.5]")

        handler.transform_selected.assert_called_once_with(None, None, [1.0, 1.0, 0.5], "MEDIAN_POINT")
        assert result == "OK"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh.get_mesh_handler")
    def test_invalid_string_returns_error(self, mock_get_mesh_handler, _mock_router_enabled):
        from server.adapters.mcp.areas.mesh import mesh_transform_selected

        handler = MagicMock()
        handler.transform_selected.return_value = "OK"
        mock_get_mesh_handler.return_value = handler

        result = mesh_transform_selected.fn(self.mock_ctx, scale="invalid")

        handler.transform_selected.assert_not_called()
        assert "Invalid coordinate format" in result

