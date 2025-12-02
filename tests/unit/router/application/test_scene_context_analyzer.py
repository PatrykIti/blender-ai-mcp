"""
Unit tests for Scene Context Analyzer.

Tests for SceneContextAnalyzer implementation.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from server.router.application.analyzers.scene_context_analyzer import SceneContextAnalyzer
from server.router.domain.entities.scene_context import SceneContext, ObjectInfo, TopologyInfo


def make_rpc_response(result, status="ok"):
    """Helper to create mock RpcResponse."""
    response = MagicMock()
    response.status = status
    response.result = result
    return response


class TestSceneContextAnalyzerBasic:
    """Test basic analyzer functionality."""

    def test_create_analyzer(self):
        """Test creating analyzer without RPC client."""
        analyzer = SceneContextAnalyzer()

        assert analyzer is not None

    def test_create_analyzer_with_rpc(self):
        """Test creating analyzer with RPC client."""
        mock_rpc = MagicMock()
        analyzer = SceneContextAnalyzer(rpc_client=mock_rpc)

        assert analyzer is not None

    def test_set_rpc_client(self):
        """Test setting RPC client after creation."""
        analyzer = SceneContextAnalyzer()
        mock_rpc = MagicMock()

        analyzer.set_rpc_client(mock_rpc)

        # Should be able to use the client now
        assert analyzer._rpc_client is mock_rpc


class TestSceneContextAnalyzerCache:
    """Test caching functionality."""

    def test_cache_initially_empty(self):
        """Test that cache is initially empty."""
        analyzer = SceneContextAnalyzer()

        cached = analyzer.get_cached()

        assert cached is None

    def test_invalidate_cache(self):
        """Test cache invalidation."""
        analyzer = SceneContextAnalyzer()
        # Manually set cache
        analyzer._cached_context = SceneContext.empty()
        analyzer._cache_timestamp = datetime.now()

        analyzer.invalidate_cache()

        assert analyzer.get_cached() is None

    def test_cache_expiry(self):
        """Test that cache expires after TTL."""
        analyzer = SceneContextAnalyzer(cache_ttl=0.1)
        analyzer._cached_context = SceneContext.empty()
        analyzer._cache_timestamp = datetime.now() - timedelta(seconds=1)

        cached = analyzer.get_cached()

        assert cached is None

    def test_cache_valid_within_ttl(self):
        """Test that cache is valid within TTL."""
        analyzer = SceneContextAnalyzer(cache_ttl=10.0)
        context = SceneContext.empty()
        analyzer._cached_context = context
        analyzer._cache_timestamp = datetime.now()

        cached = analyzer.get_cached()

        assert cached is context


class TestSceneContextAnalyzerWithoutRPC:
    """Test analyzer behavior without RPC client."""

    def test_analyze_without_rpc_returns_empty(self):
        """Test analyze returns empty context without RPC."""
        analyzer = SceneContextAnalyzer()

        context = analyzer.analyze()

        assert context.mode == "OBJECT"
        assert context.active_object is None

    def test_get_mode_without_rpc(self):
        """Test get_mode returns OBJECT without RPC."""
        analyzer = SceneContextAnalyzer()

        mode = analyzer.get_mode()

        assert mode == "OBJECT"

    def test_has_selection_without_rpc(self):
        """Test has_selection returns False without RPC."""
        analyzer = SceneContextAnalyzer()

        has_sel = analyzer.has_selection()

        assert has_sel is False


class TestSceneContextAnalyzerWithRPC:
    """Test analyzer behavior with mocked RPC client."""

    def test_get_mode_from_rpc(self):
        """Test get_mode retrieves mode from RPC."""
        mock_rpc = MagicMock()
        mock_rpc.send_request.return_value = make_rpc_response({"mode": "EDIT"})
        analyzer = SceneContextAnalyzer(rpc_client=mock_rpc)

        mode = analyzer.get_mode()

        assert mode == "EDIT"
        mock_rpc.send_request.assert_called_once()

    def test_has_selection_from_rpc(self):
        """Test has_selection from RPC."""
        mock_rpc = MagicMock()
        # Addon format: scene.list_selection returns selected_object_names list
        mock_rpc.send_request.return_value = make_rpc_response({
            "selected_object_names": ["Cube"],
            "mode": "OBJECT",
        })
        analyzer = SceneContextAnalyzer(rpc_client=mock_rpc)

        has_sel = analyzer.has_selection()

        assert has_sel is True

    def test_analyze_parses_response(self):
        """Test analyze parses full RPC response from multiple calls."""
        mock_rpc = MagicMock()

        # Mock responses for different RPC methods
        # Addon returns active_object and selected_object_names from scene.get_mode
        def mock_send_request(method, params=None):
            if method == "scene.get_mode":
                return make_rpc_response({
                    "mode": "OBJECT",
                    "active_object": "Cube",
                    "selected_object_names": ["Cube"],
                })
            elif method == "scene.list_objects":
                return make_rpc_response([
                    {
                        "name": "Cube",
                        "type": "MESH",
                        "location": [0.0, 0.0, 0.0],
                    }
                ])
            elif method == "scene.inspect_object":
                return make_rpc_response({
                    "dimensions": [2.0, 2.0, 2.0],
                    "material_slots": [{"material_name": "Material"}],
                    "modifiers": [],
                })
            return make_rpc_response({})

        mock_rpc.send_request.side_effect = mock_send_request
        analyzer = SceneContextAnalyzer(rpc_client=mock_rpc)

        context = analyzer.analyze()

        assert context.mode == "OBJECT"
        assert context.active_object == "Cube"
        assert len(context.objects) == 1
        assert context.objects[0].name == "Cube"
        # Topology only fetched in EDIT mode, so None in OBJECT mode
        assert context.topology is None

    def test_rpc_error_returns_empty(self):
        """Test that RPC error returns empty context."""
        mock_rpc = MagicMock()
        mock_rpc.send_request.side_effect = Exception("Connection failed")
        analyzer = SceneContextAnalyzer(rpc_client=mock_rpc)

        context = analyzer.analyze()

        assert context.mode == "OBJECT"
        assert context.active_object is None


class TestSceneContextAnalyzerParseData:
    """Test analyze_from_data method."""

    def test_analyze_from_data_basic(self):
        """Test parsing basic scene data."""
        analyzer = SceneContextAnalyzer()
        data = {
            "mode": "EDIT",
            "active_object": "Cube",
            "selected_objects": ["Cube"],
        }

        context = analyzer.analyze_from_data(data)

        assert context.mode == "EDIT"
        assert context.active_object == "Cube"

    def test_analyze_from_data_with_objects(self):
        """Test parsing data with objects."""
        analyzer = SceneContextAnalyzer()
        data = {
            "mode": "OBJECT",
            "active_object": "Sphere",
            "objects": [
                {
                    "name": "Sphere",
                    "type": "MESH",
                    "dimensions": [1.0, 1.0, 1.0],
                    "active": True,
                }
            ],
        }

        context = analyzer.analyze_from_data(data)

        assert len(context.objects) == 1
        assert context.objects[0].name == "Sphere"
        assert context.proportions is not None  # Should calculate proportions

    def test_analyze_from_data_with_topology(self):
        """Test parsing data with topology."""
        analyzer = SceneContextAnalyzer()
        data = {
            "mode": "EDIT",
            "topology": {
                "vertices": 100,
                "edges": 200,
                "faces": 50,
                "selected_verts": 10,
            },
        }

        context = analyzer.analyze_from_data(data)

        assert context.topology.vertices == 100
        assert context.topology.selected_verts == 10

    def test_analyze_from_data_calculates_proportions(self):
        """Test that proportions are calculated from object dimensions."""
        analyzer = SceneContextAnalyzer()
        data = {
            "mode": "OBJECT",
            "objects": [
                {
                    "name": "TallTower",
                    "type": "MESH",
                    "dimensions": [0.5, 0.5, 5.0],
                    "active": True,
                }
            ],
        }

        context = analyzer.analyze_from_data(data)

        assert context.proportions is not None
        assert context.proportions.is_tall is True


class TestSceneContextAnalyzerCacheUpdate:
    """Test cache update behavior."""

    def test_analyze_updates_cache(self):
        """Test that analyze updates the cache."""
        mock_rpc = MagicMock()

        # Mock multiple RPC methods
        # Addon returns active_object and selected_object_names from scene.get_mode
        def mock_send_request(method, params=None):
            if method == "scene.get_mode":
                return make_rpc_response({
                    "mode": "OBJECT",
                    "active_object": "Cube",
                    "selected_object_names": ["Cube"],
                })
            elif method == "scene.list_objects":
                return make_rpc_response([{"name": "Cube", "type": "MESH", "location": [0.0, 0.0, 0.0]}])
            elif method == "scene.inspect_object":
                return make_rpc_response({"dimensions": [2.0, 2.0, 2.0], "material_slots": [], "modifiers": []})
            return make_rpc_response({})

        mock_rpc.send_request.side_effect = mock_send_request
        analyzer = SceneContextAnalyzer(rpc_client=mock_rpc, cache_ttl=10.0)

        # First call - should hit RPC:
        # 1. get_mode (mode, active_object, selected_object_names)
        # 2. list_objects (object list)
        # 3. inspect_object (for active object dimensions)
        # 4. inspect_object (for active object materials/modifiers)
        context1 = analyzer.analyze()
        first_call_count = mock_rpc.send_request.call_count
        assert first_call_count == 4  # 4 RPC method calls

        # Second call - should use cache
        context2 = analyzer.analyze()
        assert mock_rpc.send_request.call_count == first_call_count  # No additional calls

    def test_analyze_refreshes_expired_cache(self):
        """Test that analyze refreshes expired cache."""
        mock_rpc = MagicMock()

        # Mock multiple RPC methods
        # Addon returns active_object and selected_object_names from scene.get_mode
        def mock_send_request(method, params=None):
            if method == "scene.get_mode":
                return make_rpc_response({
                    "mode": "OBJECT",
                    "active_object": "Cube",
                    "selected_object_names": ["Cube"],
                })
            elif method == "scene.list_objects":
                return make_rpc_response([{"name": "Cube", "type": "MESH", "location": [0.0, 0.0, 0.0]}])
            elif method == "scene.inspect_object":
                return make_rpc_response({"dimensions": [2.0, 2.0, 2.0], "material_slots": [], "modifiers": []})
            return make_rpc_response({})

        mock_rpc.send_request.side_effect = mock_send_request
        analyzer = SceneContextAnalyzer(rpc_client=mock_rpc, cache_ttl=0.0)

        # First call - 4 RPC calls
        analyzer.analyze()
        first_call_count = mock_rpc.send_request.call_count

        # Expire the cache
        analyzer._cache_timestamp = datetime.now() - timedelta(seconds=1)

        # Second call should refresh - another 4 RPC calls
        analyzer.analyze()

        assert mock_rpc.send_request.call_count == first_call_count * 2  # 8 calls total
