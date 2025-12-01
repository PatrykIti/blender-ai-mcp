"""
Unit tests for Scene Context Analyzer.

Tests for SceneContextAnalyzer implementation.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from server.router.application.analyzers.scene_context_analyzer import SceneContextAnalyzer
from server.router.domain.entities.scene_context import SceneContext, ObjectInfo, TopologyInfo


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
        mock_rpc.send_request.return_value = {"mode": "EDIT"}
        analyzer = SceneContextAnalyzer(rpc_client=mock_rpc)

        mode = analyzer.get_mode()

        assert mode == "EDIT"
        mock_rpc.send_request.assert_called_once()

    def test_has_selection_from_rpc(self):
        """Test has_selection from RPC."""
        mock_rpc = MagicMock()
        mock_rpc.send_request.return_value = {
            "selection": {"has_selection": True}
        }
        analyzer = SceneContextAnalyzer(rpc_client=mock_rpc)

        has_sel = analyzer.has_selection()

        assert has_sel is True

    def test_analyze_parses_response(self):
        """Test analyze parses full RPC response."""
        mock_rpc = MagicMock()
        mock_rpc.send_request.return_value = {
            "mode": "OBJECT",
            "active_object": "Cube",
            "selected_objects": ["Cube"],
            "objects": [
                {
                    "name": "Cube",
                    "type": "MESH",
                    "location": [0.0, 0.0, 0.0],
                    "dimensions": [2.0, 2.0, 2.0],
                    "selected": True,
                    "active": True,
                }
            ],
            "topology": {
                "vertices": 8,
                "edges": 12,
                "faces": 6,
            },
            "materials": ["Material"],
            "modifiers": [],
        }
        analyzer = SceneContextAnalyzer(rpc_client=mock_rpc)

        context = analyzer.analyze()

        assert context.mode == "OBJECT"
        assert context.active_object == "Cube"
        assert len(context.objects) == 1
        assert context.objects[0].name == "Cube"
        assert context.topology.vertices == 8

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
        mock_rpc.send_request.return_value = {
            "mode": "OBJECT",
            "active_object": "Cube",
        }
        analyzer = SceneContextAnalyzer(rpc_client=mock_rpc, cache_ttl=10.0)

        # First call - should hit RPC
        context1 = analyzer.analyze()
        assert mock_rpc.send_request.call_count == 1

        # Second call - should use cache
        context2 = analyzer.analyze()
        assert mock_rpc.send_request.call_count == 1  # No additional call

    def test_analyze_refreshes_expired_cache(self):
        """Test that analyze refreshes expired cache."""
        mock_rpc = MagicMock()
        mock_rpc.send_request.return_value = {
            "mode": "OBJECT",
            "active_object": "Cube",
        }
        analyzer = SceneContextAnalyzer(rpc_client=mock_rpc, cache_ttl=0.0)

        # First call
        analyzer.analyze()
        # Expire the cache
        analyzer._cache_timestamp = datetime.now() - timedelta(seconds=1)

        # Second call should refresh
        analyzer.analyze()

        assert mock_rpc.send_request.call_count == 2
