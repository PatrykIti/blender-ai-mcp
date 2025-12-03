"""
E2E Tests for extraction_deep_topology (TASK-044-1)

These tests require a running Blender instance with the addon loaded.
"""
import pytest
from server.application.tool_handlers.extraction_handler import ExtractionToolHandler


@pytest.fixture
def extraction_handler(rpc_client):
    """Provides an extraction handler instance using shared RPC client."""
    return ExtractionToolHandler(rpc_client)


def test_deep_topology_cube(extraction_handler):
    """Test deep topology analysis on default cube."""
    try:
        result = extraction_handler.deep_topology("Cube")

        assert "object_name" in result
        assert result["object_name"] == "Cube"
        assert "vertex_count" in result
        assert "edge_count" in result
        assert "face_count" in result
        assert "base_primitive" in result
        assert "bounding_box" in result

        print(f"✓ deep_topology on Cube: {result['vertex_count']} verts, {result['face_count']} faces")
        print(f"  Base primitive: {result['base_primitive']} ({result['primitive_confidence']})")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_deep_topology_feature_detection(extraction_handler):
    """Test feature detection in topology analysis."""
    try:
        result = extraction_handler.deep_topology("Cube")

        # Check feature flags exist
        assert "has_beveled_edges" in result
        assert "has_inset_faces" in result
        assert "has_extrusions" in result
        assert "tri_count" in result
        assert "quad_count" in result
        assert "ngon_count" in result

        print("✓ deep_topology feature detection working")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_deep_topology_not_found(extraction_handler):
    """Test deep topology on non-existent object."""
    try:
        result = extraction_handler.deep_topology("NonExistentObject12345")
        pytest.fail("Should have raised an error")

    except RuntimeError as e:
        assert "not found" in str(e).lower() or "error" in str(e).lower()
        print("✓ deep_topology: correctly handles non-existent object")
