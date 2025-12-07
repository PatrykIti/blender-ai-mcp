"""Tests for mesh_select mega tool routing and validation."""
import pytest
from unittest.mock import MagicMock, patch


class TestMeshSelectMega:
    """Test mesh_select mega tool routing."""

    def setup_method(self):
        self.mock_ctx = MagicMock()

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_select_all")
    def test_action_all_routes_to_select_all(self, mock_select_all, mock_router_enabled):
        """Test action='all' routes to _mesh_select_all with deselect=False."""
        from server.adapters.mcp.areas.mesh import mesh_select

        mock_select_all.return_value = "All selected"
        result = mesh_select.fn(self.mock_ctx, action="all")

        mock_select_all.assert_called_once_with(self.mock_ctx, deselect=False)
        assert result == "All selected"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_select_all")
    def test_action_none_routes_to_select_all_deselect(self, mock_select_all, mock_router_enabled):
        """Test action='none' routes to _mesh_select_all with deselect=True."""
        from server.adapters.mcp.areas.mesh import mesh_select

        mock_select_all.return_value = "All deselected"
        result = mesh_select.fn(self.mock_ctx, action="none")

        mock_select_all.assert_called_once_with(self.mock_ctx, deselect=True)
        assert result == "All deselected"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_select_linked")
    def test_action_linked_routes_to_select_linked(self, mock_select_linked, mock_router_enabled):
        """Test action='linked' routes to _mesh_select_linked."""
        from server.adapters.mcp.areas.mesh import mesh_select

        mock_select_linked.return_value = "Linked selected"
        result = mesh_select.fn(self.mock_ctx, action="linked")

        mock_select_linked.assert_called_once_with(self.mock_ctx)
        assert result == "Linked selected"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_select_more")
    def test_action_more_routes_to_select_more(self, mock_select_more, mock_router_enabled):
        """Test action='more' routes to _mesh_select_more."""
        from server.adapters.mcp.areas.mesh import mesh_select

        mock_select_more.return_value = "Selection expanded"
        result = mesh_select.fn(self.mock_ctx, action="more")

        mock_select_more.assert_called_once_with(self.mock_ctx)
        assert result == "Selection expanded"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_select_less")
    def test_action_less_routes_to_select_less(self, mock_select_less, mock_router_enabled):
        """Test action='less' routes to _mesh_select_less."""
        from server.adapters.mcp.areas.mesh import mesh_select

        mock_select_less.return_value = "Selection contracted"
        result = mesh_select.fn(self.mock_ctx, action="less")

        mock_select_less.assert_called_once_with(self.mock_ctx)
        assert result == "Selection contracted"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_select_boundary")
    def test_action_boundary_routes_to_select_boundary(self, mock_select_boundary, mock_router_enabled):
        """Test action='boundary' routes to _mesh_select_boundary."""
        from server.adapters.mcp.areas.mesh import mesh_select

        mock_select_boundary.return_value = "Boundary selected"
        result = mesh_select.fn(self.mock_ctx, action="boundary")

        mock_select_boundary.assert_called_once_with(self.mock_ctx, mode="EDGE")
        assert result == "Boundary selected"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_select_boundary")
    def test_action_boundary_with_vert_mode(self, mock_select_boundary, mock_router_enabled):
        """Test action='boundary' with boundary_mode='VERT'."""
        from server.adapters.mcp.areas.mesh import mesh_select

        mock_select_boundary.return_value = "Boundary vertices selected"
        result = mesh_select.fn(self.mock_ctx, action="boundary", boundary_mode="VERT")

        mock_select_boundary.assert_called_once_with(self.mock_ctx, mode="VERT")
        assert result == "Boundary vertices selected"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    def test_invalid_action_returns_error(self, mock_router_enabled):
        """Test invalid action returns helpful error message."""
        from server.adapters.mcp.areas.mesh import mesh_select

        result = mesh_select.fn(self.mock_ctx, action="invalid")

        assert "Unknown action" in result
        assert "invalid" in result
        assert "all" in result
        assert "none" in result
        assert "linked" in result
        assert "more" in result
        assert "less" in result
        assert "boundary" in result
