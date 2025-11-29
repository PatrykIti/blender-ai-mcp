"""Tests for mesh_select_targeted mega tool routing and validation."""
import pytest
from unittest.mock import MagicMock, patch


class TestMeshSelectTargetedMega:
    """Test mesh_select_targeted mega tool routing and parameter validation."""

    def setup_method(self):
        self.mock_ctx = MagicMock()

    @patch("server.adapters.mcp.areas.mesh._mesh_select_by_index")
    def test_action_by_index_routes_correctly(self, mock_select_by_index):
        """Test action='by_index' routes to _mesh_select_by_index."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        mock_select_by_index.return_value = "Selected by index"
        result = mesh_select_targeted.fn(
            self.mock_ctx,
            action="by_index",
            indices=[0, 1, 2],
            element_type="VERT",
            selection_mode="SET"
        )

        mock_select_by_index.assert_called_once_with(
            self.mock_ctx, [0, 1, 2], "VERT", "SET"
        )
        assert result == "Selected by index"

    def test_action_by_index_missing_indices_returns_error(self):
        """Test action='by_index' without indices returns error."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        result = mesh_select_targeted.fn(self.mock_ctx, action="by_index")

        assert "Error" in result
        assert "indices" in result

    @patch("server.adapters.mcp.areas.mesh._mesh_select_loop")
    def test_action_loop_routes_correctly(self, mock_select_loop):
        """Test action='loop' routes to _mesh_select_loop."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        mock_select_loop.return_value = "Loop selected"
        result = mesh_select_targeted.fn(
            self.mock_ctx,
            action="loop",
            edge_index=5
        )

        mock_select_loop.assert_called_once_with(self.mock_ctx, 5)
        assert result == "Loop selected"

    def test_action_loop_missing_edge_index_returns_error(self):
        """Test action='loop' without edge_index returns error."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        result = mesh_select_targeted.fn(self.mock_ctx, action="loop")

        assert "Error" in result
        assert "edge_index" in result

    @patch("server.adapters.mcp.areas.mesh._mesh_select_ring")
    def test_action_ring_routes_correctly(self, mock_select_ring):
        """Test action='ring' routes to _mesh_select_ring."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        mock_select_ring.return_value = "Ring selected"
        result = mesh_select_targeted.fn(
            self.mock_ctx,
            action="ring",
            edge_index=3
        )

        mock_select_ring.assert_called_once_with(self.mock_ctx, 3)
        assert result == "Ring selected"

    def test_action_ring_missing_edge_index_returns_error(self):
        """Test action='ring' without edge_index returns error."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        result = mesh_select_targeted.fn(self.mock_ctx, action="ring")

        assert "Error" in result
        assert "edge_index" in result

    @patch("server.adapters.mcp.areas.mesh._mesh_select_by_location")
    def test_action_by_location_routes_correctly(self, mock_select_by_location):
        """Test action='by_location' routes to _mesh_select_by_location."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        mock_select_by_location.return_value = "Selected by location"
        result = mesh_select_targeted.fn(
            self.mock_ctx,
            action="by_location",
            axis="Z",
            min_coord=0.5,
            max_coord=2.0,
            element_type="VERT"
        )

        mock_select_by_location.assert_called_once_with(
            self.mock_ctx, "Z", 0.5, 2.0, "VERT"
        )
        assert result == "Selected by location"

    def test_action_by_location_missing_axis_returns_error(self):
        """Test action='by_location' without axis returns error."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        result = mesh_select_targeted.fn(
            self.mock_ctx,
            action="by_location",
            min_coord=0.5,
            max_coord=2.0
        )

        assert "Error" in result
        assert "axis" in result or "min_coord" in result or "max_coord" in result

    def test_action_by_location_missing_coords_returns_error(self):
        """Test action='by_location' without coords returns error."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        result = mesh_select_targeted.fn(
            self.mock_ctx,
            action="by_location",
            axis="Z"
        )

        assert "Error" in result

    def test_invalid_action_returns_error(self):
        """Test invalid action returns helpful error message."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        result = mesh_select_targeted.fn(self.mock_ctx, action="invalid")

        assert "Unknown action" in result
        assert "invalid" in result
        assert "by_index" in result
        assert "loop" in result
        assert "ring" in result
        assert "by_location" in result

    @patch("server.adapters.mcp.areas.mesh._mesh_select_by_index")
    def test_action_by_index_with_face_type(self, mock_select_by_index):
        """Test action='by_index' with element_type='FACE'."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        mock_select_by_index.return_value = "Faces selected"
        result = mesh_select_targeted.fn(
            self.mock_ctx,
            action="by_index",
            indices=[0, 1],
            element_type="FACE",
            selection_mode="ADD"
        )

        mock_select_by_index.assert_called_once_with(
            self.mock_ctx, [0, 1], "FACE", "ADD"
        )
        assert result == "Faces selected"
