"""Tests for mesh_select_targeted mega tool routing and validation."""

from unittest.mock import MagicMock, patch

from server.adapters.mcp.contracts.mesh import MeshSelectionResponseContract


class TestMeshSelectTargetedMega:
    """Test mesh_select_targeted mega tool routing and parameter validation."""

    def setup_method(self):
        self.mock_ctx = MagicMock()

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_select_by_index")
    def test_action_by_index_routes_correctly(self, mock_select_by_index, mock_router_enabled):
        """Test action='by_index' routes to _mesh_select_by_index."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        mock_select_by_index.return_value = "Selected by index"
        callable_mesh_select_targeted = getattr(mesh_select_targeted, "fn", mesh_select_targeted)
        result = callable_mesh_select_targeted(
            self.mock_ctx, action="by_index", indices=[0, 1, 2], element_type="VERT", selection_mode="SET"
        )

        mock_select_by_index.assert_called_once_with(self.mock_ctx, [0, 1, 2], "VERT", "SET")
        assert isinstance(result, MeshSelectionResponseContract)
        assert result.payload["message"] == "Selected by index"
        assert result.payload["operation"]["indices"] == [0, 1, 2]

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    def test_action_by_index_missing_indices_returns_error(self, mock_router_enabled):
        """Test action='by_index' without indices returns error."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        callable_mesh_select_targeted = getattr(mesh_select_targeted, "fn", mesh_select_targeted)
        result = callable_mesh_select_targeted(self.mock_ctx, action="by_index")

        assert isinstance(result, MeshSelectionResponseContract)
        assert "Error" in result.error
        assert "indices" in result.error

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_select_loop")
    def test_action_loop_routes_correctly(self, mock_select_loop, mock_router_enabled):
        """Test action='loop' routes to _mesh_select_loop."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        mock_select_loop.return_value = "Loop selected"
        callable_mesh_select_targeted = getattr(mesh_select_targeted, "fn", mesh_select_targeted)
        result = callable_mesh_select_targeted(self.mock_ctx, action="loop", edge_index=5)

        mock_select_loop.assert_called_once_with(self.mock_ctx, 5)
        assert isinstance(result, MeshSelectionResponseContract)
        assert result.payload["message"] == "Loop selected"
        assert result.payload["operation"]["edge_index"] == 5

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    def test_action_loop_missing_edge_index_returns_error(self, mock_router_enabled):
        """Test action='loop' without edge_index returns error."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        callable_mesh_select_targeted = getattr(mesh_select_targeted, "fn", mesh_select_targeted)
        result = callable_mesh_select_targeted(self.mock_ctx, action="loop")

        assert isinstance(result, MeshSelectionResponseContract)
        assert "Error" in result.error
        assert "edge_index" in result.error

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_select_ring")
    def test_action_ring_routes_correctly(self, mock_select_ring, mock_router_enabled):
        """Test action='ring' routes to _mesh_select_ring."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        mock_select_ring.return_value = "Ring selected"
        callable_mesh_select_targeted = getattr(mesh_select_targeted, "fn", mesh_select_targeted)
        result = callable_mesh_select_targeted(self.mock_ctx, action="ring", edge_index=3)

        mock_select_ring.assert_called_once_with(self.mock_ctx, 3)
        assert isinstance(result, MeshSelectionResponseContract)
        assert result.payload["message"] == "Ring selected"
        assert result.payload["operation"]["edge_index"] == 3

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    def test_action_ring_missing_edge_index_returns_error(self, mock_router_enabled):
        """Test action='ring' without edge_index returns error."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        callable_mesh_select_targeted = getattr(mesh_select_targeted, "fn", mesh_select_targeted)
        result = callable_mesh_select_targeted(self.mock_ctx, action="ring")

        assert isinstance(result, MeshSelectionResponseContract)
        assert "Error" in result.error
        assert "edge_index" in result.error

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_select_by_location")
    def test_action_by_location_routes_correctly(self, mock_select_by_location, mock_router_enabled):
        """Test action='by_location' routes to _mesh_select_by_location."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        mock_select_by_location.return_value = "Selected by location"
        callable_mesh_select_targeted = getattr(mesh_select_targeted, "fn", mesh_select_targeted)
        result = callable_mesh_select_targeted(
            self.mock_ctx, action="by_location", axis="Z", min_coord=0.5, max_coord=2.0, element_type="VERT"
        )

        mock_select_by_location.assert_called_once_with(self.mock_ctx, "Z", 0.5, 2.0, "VERT")
        assert isinstance(result, MeshSelectionResponseContract)
        assert result.payload["message"] == "Selected by location"
        assert result.payload["operation"]["axis"] == "Z"

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    def test_action_by_location_missing_axis_returns_error(self, mock_router_enabled):
        """Test action='by_location' without axis returns error."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        callable_mesh_select_targeted = getattr(mesh_select_targeted, "fn", mesh_select_targeted)
        result = callable_mesh_select_targeted(self.mock_ctx, action="by_location", min_coord=0.5, max_coord=2.0)

        assert isinstance(result, MeshSelectionResponseContract)
        assert "Error" in result.error
        assert "axis" in result.error or "min_coord" in result.error or "max_coord" in result.error

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    def test_action_by_location_missing_coords_returns_error(self, mock_router_enabled):
        """Test action='by_location' without coords returns error."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        callable_mesh_select_targeted = getattr(mesh_select_targeted, "fn", mesh_select_targeted)
        result = callable_mesh_select_targeted(self.mock_ctx, action="by_location", axis="Z")

        assert isinstance(result, MeshSelectionResponseContract)
        assert "Error" in result.error

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    def test_invalid_action_returns_error(self, mock_router_enabled):
        """Test invalid action returns helpful error message."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        callable_mesh_select_targeted = getattr(mesh_select_targeted, "fn", mesh_select_targeted)
        result = callable_mesh_select_targeted(self.mock_ctx, action="invalid")

        assert isinstance(result, MeshSelectionResponseContract)
        assert "Unknown action" in result.error
        assert "invalid" in result.error
        assert "by_index" in result.error
        assert "loop" in result.error
        assert "ring" in result.error
        assert "by_location" in result.error

    @patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
    @patch("server.adapters.mcp.areas.mesh._mesh_select_by_index")
    def test_action_by_index_with_face_type(self, mock_select_by_index, mock_router_enabled):
        """Test action='by_index' with element_type='FACE'."""
        from server.adapters.mcp.areas.mesh import mesh_select_targeted

        mock_select_by_index.return_value = "Faces selected"
        callable_mesh_select_targeted = getattr(mesh_select_targeted, "fn", mesh_select_targeted)
        result = callable_mesh_select_targeted(
            self.mock_ctx, action="by_index", indices=[0, 1], element_type="FACE", selection_mode="ADD"
        )

        mock_select_by_index.assert_called_once_with(self.mock_ctx, [0, 1], "FACE", "ADD")
        assert isinstance(result, MeshSelectionResponseContract)
        assert result.payload["message"] == "Faces selected"
        assert result.payload["operation"]["element_type"] == "FACE"
